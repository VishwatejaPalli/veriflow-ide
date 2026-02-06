from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

class App:
    def __init__(self):
        self.qt_app = QApplication([])
        self.window = MainWindow()

    def run(self):
        print("OpenHDL-IDE starting...")
        self.window.show()
        self.qt_app.exec()
