"""
メインエントリーポイント
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QStyleFactory
from gui import TranscriptionGUI

def main():
    # 警告メッセージを抑制
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
    
    # アプリケーションの初期化
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    
    # フォントエイリアスの警告を抑制
    app.setDesktopSettingsAware(False)
    
    # ウィンドウの表示
    window = TranscriptionGUI()
    window.show()
    
    # イベントループの開始
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
