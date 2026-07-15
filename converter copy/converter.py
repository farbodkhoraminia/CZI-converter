# converter/converter.py
import gc
import logging
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import numpy as np
import requests
from PIL import Image

try:
    from pma_python import core
except Exception:  # pragma: no cover - optional dependency path
    core = None

try:
    import multiresolutionimageinterface as mir
except Exception:  # pragma: no cover - optional dependency path
    mir = None

try:
    from czifile import CziFile
    from tifffile import imwrite
except Exception:  # pragma: no cover - optional dependency path
    CziFile = None
    imwrite = None

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
        if core is None:
            logging.error("pma_python is not available; cannot retrieve tiles.")
            return None

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

    def _fallback_convert_slide(self, inp, out):
        if CziFile is None or imwrite is None:
            raise RuntimeError("Fallback CZI reader is unavailable. Install 'czifile' and 'tifffile'.")

        logging.info("Using built-in fallback CZI reader for %s", inp)
        with CziFile(inp) as czi:
            image = czi.asarray()

        if image.ndim == 2:
            image = image[..., None]
        if image.ndim == 3 and image.shape[0] in (1, 3, 4):
            image = np.transpose(image, (1, 2, 0))
        if image.dtype != np.uint8:
            image = image.astype(np.uint8)

        imwrite(out, image, photometric='rgb' if image.ndim == 3 else 'minisblack')
        return out

    def convert_slide(self, inp, out):
        cur_file = inp
        try:
            result = self._fallback_convert_slide(inp, out)
            logging.info("Successfully converted %s to %s using fallback reader", inp, result)
            return result
        except Exception as e:
            logging.error(f"Failed to convert {inp}: {e}", exc_info=True)
            return None
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

    def run(self, max_files=None):
        processed_files = self.load_processed_files()
        threading.Thread(target=self.monitor_progress, daemon=True).start()
        logging.info("Started monitoring thread.")

        processed_count = 0
        while True:
            try:
                czi_files = sorted([f for f in self.config.INPUT_FOLDER.iterdir() if f.suffix.lower() == '.czi'])
                if not czi_files:
                    logging.info("No .czi files found in %s; waiting.", self.config.INPUT_FOLDER)
                    time.sleep(self.config.CHECK_INTERVAL_SECONDS)
                    continue

                for cf in czi_files:
                    if max_files is not None and processed_count >= max_files:
                        logging.info("Reached the requested limit of %s image(s). Stopping.", max_files)
                        return

                    cf_path = cf.resolve()
                    if str(cf_path) in processed_files:
                        continue

                    logging.info("Starting conversion for %s", cf_path)
                    run_pma_start(self.config.PMA_EXECUTABLE_PATH, cf_path)
                    time.sleep(1)
                    out_tif = self.config.OUTPUT_FOLDER / f"{cf.stem}.tif"
                    self.convert_slide(cf_path, out_tif)
                    processed_files.add(str(cf_path))
                    self.save_processed_files(processed_files)
                    processed_count += 1
                    logging.info("✓ Completed image %s/%s in this run.", processed_count, max_files or 'all')

                if max_files is not None and processed_count >= max_files:
                    logging.info("Reached the requested limit of %s image(s). Stopping.", max_files)
                    return

                time.sleep(self.config.CHECK_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logging.info("Shutdown signal received. Exiting.")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(self.config.CHECK_INTERVAL_SECONDS)
