# main.py
import argparse
from pathlib import Path

from converter.config import Config
from converter.converter import SlideConverter


def parse_args():
    parser = argparse.ArgumentParser(description='Run the CZI to TIFF converter.')
    parser.add_argument('--input-folder', dest='input_folder', help='Path to the folder containing .czi files')
    parser.add_argument('--nb-imgs', dest='nb_imgs', type=int, default=None, help='Maximum number of images to process in this run')
    parser.add_argument('--workers', dest='workers', type=int, default=None, help='Number of worker threads to use')
    return parser.parse_args()


def main():
    try:
        args = parse_args()
        config = Config('config.yaml')

        if args.input_folder:
            config.INPUT_FOLDER = Path(args.input_folder).expanduser().resolve()
        if args.workers is not None:
            config.WORKERS = args.workers
        if args.nb_imgs is not None:
            config.MAX_IMAGES = args.nb_imgs

        converter = SlideConverter(config)
        converter.run(max_files=args.nb_imgs)
    except Exception as e:
        print(f"Error initializing the converter: {e}")


if __name__ == "__main__":
    main()
