from sys import (
    argv,
    exit,
)
from PyQt6.QtWidgets import QApplication
from imagecolorpicker.mainwindow import MainWindow

if __name__ == '__main__':
    application: QApplication = QApplication(argv)

    mainWindow = MainWindow()
    mainWindow.show()

    exit(application.exec())
