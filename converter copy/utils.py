# converter/utils.py
import logging
import subprocess
from pathlib import Path


def run_pma_start(pma_executable_path: Path, czi_file: Path):
    """
    Start the PMA executable if it exists. On Linux systems where the PMA
    executable is not available, this simply logs and returns without error.
    """
    if pma_executable_path is None:
        logging.warning("PMA executable path is not configured; skipping PMA startup.")
        return False

    if not pma_executable_path.exists():
        logging.warning(f"PMA executable not found at {pma_executable_path}; skipping PMA startup.")
        return False

    try:
        subprocess.Popen(
            [str(pma_executable_path), str(czi_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logging.info(f"Started PMA with file: {czi_file}")
        return True
    except Exception as e:
        logging.error(f"PMA.start error for {czi_file}: {e}", exc_info=True)
        return False
