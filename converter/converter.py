# converter/converter.py
import os
import sys
import time
import logging
import threading
import gc
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image
import requests
import numpy as np
from pma_python import core
import multiresolutionimageinterface as mir

from .utils import run_pma_start

class SlideConverter:
    def __init__(self, config):
        self.config = config
        self.processing_status = {}
        self.status_lock = threading.Lock()
        self.setup_logging()
        self.update_sys_path()
        self.ensure_directories()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.config.LOG_FILE,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Logging initialized.")

    def update_sys_path(self):
        sys.path = [p for p in sys.path if "ASAP" not in p]
        sys.path.insert(0, str(self.config.ASAP_BIN_PATH))
        logging.info(f"Updated sys.path with ASAP_BIN_PATH: {self.config.ASAP_BIN_PATH}")

    def ensure_directories(self):
        """
        Ensures that the output directory exists.
        """
        self.config.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        self.config.INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
        logging.info("Verified input and output directories.")

    def get_tile(self, slide, x, y, z, session):
        pma_session_id = "SDK.Python"
        pma_url = core._pma_url(pma_session_id) + "tile"
        params = {
            "sessionID": pma_session_id,
            "channels": 0,
            "timeframe": 0,
            "layer": 0,
            "pathOrUid": str(slide),
            "x": int(round(x)),
            "y": int(round(y)),
            "z": int(round(z)),
            "format": "jpg",
            "quality": 100,
            "cache": "false"
        }
        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = session.get(pma_url, params=params, timeout=30)
                response.raise_for_status()
                return Image.open(BytesIO(response.content))
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed to get tile ({x}, {y}, {z}): {e}")
                time.sleep(1)
        logging.error(f"Failed to retrieve tile ({x}, {y}, {z}) after {self.config.MAX_RETRIES} attempts.")
        return None

    def process_tile(self, xi, yi, tsize, inp, z, sess, cur_file):
        tile = self.get_tile(inp, xi, yi, z, sess)
        if tile is None:
            return None, None, None
        patch = np.array(tile, dtype=np.uint8).flatten()
        with self.processing_status[cur_file]['lock']:
            self.processing_status[cur_file]['last_tile_count'] += 1
            self.processing_status[cur_file]['last_progress_time'] = time.time()
        return patch, xi * tsize, yi * tsize

    def convert_slide(self, inp, out):
        cur_file = inp
        try:
            slide_info = core.get_slide_info(inp)
            zoom_info = core.get_zoomlevels_dict(inp)
            z = max(zoom_info)
            x_range, y_range, total_tiles = zoom_info[z][0], zoom_info[z][1], zoom_info[z][-1]
            dim_x, dim_y, tile_size = slide_info["Width"], slide_info["Height"], slide_info["TileSize"]
            spx, spy = slide_info["MicrometresPerPixelX"], slide_info["MicrometresPerPixelY"]

            sp = mir.vector_double()
            sp.push_back(spx)
            sp.push_back(spy)

            writer = mir.MultiResolutionImageWriter()
            writer.openFile(str(out))
            writer.setTileSize(tile_size)
            writer.setCompression(mir.Compression_JPEG)
            writer.setJPEGQuality(75)
            writer.setDataType(mir.DataType_UChar)
            writer.setColorType(mir.ColorType_RGB)
            writer.writeImageInformation(dim_x, dim_y)
            writer.setSpacing(sp)

            sess = requests.Session()
            with self.status_lock:
                self.processing_status[cur_file] = {
                    'last_tile_count': 0,
                    'last_progress_time': time.time(),
                    'lock': threading.Lock()
                }

            with ThreadPoolExecutor(max_workers=self.config.WORKERS) as executor:
                futures = {
                    executor.submit(self.process_tile, xi, yi, tile_size, inp, z, sess, cur_file): (xi, yi)
                    for yi in range(y_range) for xi in range(x_range)
                }

                cnt = 0
                for future in futures:
                    tile_data, xo, yo = future.result()
                    if tile_data is None:
                        continue
                    writer.writeBaseImagePartToLocation(tile_data, xo, yo)
                    cnt += 1
                    print(f"Processed {cnt}/{total_tiles} tiles")

            writer.finishImage()
            sess.close()
            logging.info(f"Successfully converted {inp} to {out}")

        except Exception as e:
            logging.error(f"Failed to convert {inp}: {e}", exc_info=True)
        finally:
            with self.status_lock:
                if cur_file in self.processing_status:
                    del self.processing_status[cur_file]
            gc.collect()

    def load_processed_files(self):
        if not self.config.PROCESSED_FILES_RECORD.is_file():
            return set()
        with open(self.config.PROCESSED_FILES_RECORD, 'r') as f:
            return set(line.strip() for line in f)

    def save_processed_files(self, processed_files):
        with open(self.config.PROCESSED_FILES_RECORD, 'w') as f:
            for file in processed_files:
                f.write(f"{file}\n")

    def monitor_progress(self):
        while True:
            time.sleep(self.config.STALL_TIMEOUT_SECONDS)
            with self.status_lock:
                for fp, st in list(self.processing_status.items()):
                    with st['lock']:
                        if time.time() - st['last_progress_time'] > self.config.STALL_TIMEOUT_SECONDS:
                            logging.warning(f"Stall detected: {fp}. Rerunning PMA.start.")
                            run_pma_start(self.config.PMA_EXECUTABLE_PATH, fp)
                            st['last_progress_time'] = time.time()

    def run(self):
        processed_files = self.load_processed_files()
        threading.Thread(target=self.monitor_progress, daemon=True).start()
        logging.info("Started monitoring thread.")

        while True:
            try:
                czi_files = [f for f in self.config.INPUT_FOLDER.iterdir() if f.suffix.lower() == '.czi']
                for cf in czi_files:
                    cf_path = cf.resolve()
                    if str(cf_path) in processed_files:
                        continue
                    run_pma_start(self.config.PMA_EXECUTABLE_PATH, cf_path)
                    time.sleep(5)
                    out_tif = self.config.OUTPUT_FOLDER / f"{cf.stem}.tif"
                    self.convert_slide(cf_path, out_tif)
                    processed_files.add(str(cf_path))
                    self.save_processed_files(processed_files)
                time.sleep(self.config.CHECK_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logging.info("Shutdown signal received. Exiting.")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(self.config.CHECK_INTERVAL_SECONDS)
