"""
メインエントリーポイント
"""
import sys
from PyQt6.QtWidgets import QApplication, QStyleFactory
from gui import TranscriptionGUI

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = TranscriptionGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
