# converter/config.py
import os
from pathlib import Path

import yaml


class Config:
    def __init__(self, config_path='config.yaml'):
        self.config_path = Path(config_path).expanduser()
        self.load_config()

    def load_config(self):
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Configuration file {self.config_path} not found.")
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file) or {}

        asap_path = config.get('ASAP_BIN_PATH')
        pma_path = config.get('PMA_EXECUTABLE_PATH')

        self.ASAP_BIN_PATH = Path(asap_path).expanduser() if asap_path else Path('/opt/ASAP/bin')
        self.PMA_EXECUTABLE_PATH = Path(pma_path).expanduser() if pma_path else Path('/opt/pathomation/PMA.start')
        self.INPUT_FOLDER = Path(config.get('INPUT_FOLDER', 'data/input')).expanduser()
        self.OUTPUT_FOLDER = Path(config.get('OUTPUT_FOLDER', 'data/output')).expanduser()
        self.PROCESSED_FILES_RECORD = Path(config.get('PROCESSED_FILES_RECORD', 'data/processed_files.txt')).expanduser()
        self.CHECK_INTERVAL_SECONDS = config.get('CHECK_INTERVAL_SECONDS', 10)
        self.STALL_TIMEOUT_SECONDS = config.get('STALL_TIMEOUT_SECONDS', 2)
        self.MAX_RETRIES = config.get('MAX_RETRIES', 3)
        self.LOG_FILE = Path(config.get('LOG_FILE', 'logs/conversion_automation.log')).expanduser()
        self.WORKERS = config.get('WORKERS', 12)
