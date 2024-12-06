# main.py
from converter.config import Config
from converter.converter import SlideConverter

def main():
    try:
        config = Config('config.yaml')
        converter = SlideConverter(config)
        converter.run()
    except Exception as e:
        print(f"Error initializing the converter: {e}")

if __name__ == "__main__":
    main()
