import logging

from src.UIgradio import create_ui

def main():
    logging.basicConfig(level = logging.INFO)
    demo = create_ui()
    demo.launch(share = True, inbrowser = True)

if __name__ == "__main__":
    main()
