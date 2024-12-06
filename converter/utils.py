# converter/utils.py
import subprocess
import logging
from pathlib import Path

def run_pma_start(pma_executable_path: Path, czi_file: Path):
    """
    Starts the PMA executable with the given CZI file.

    Args:
        pma_executable_path (Path): Path to the PMA executable.
        czi_file (Path): Path to the CZI file to be processed.
    """
    try:
        subprocess.Popen(
            [str(pma_executable_path), str(czi_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f"Started PMA with file: {czi_file}")
    except Exception as e:
        logging.error(f"PMA.start error for {czi_file}: {e}", exc_info=True)
