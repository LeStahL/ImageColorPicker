from PyQt6.QtWidgets import QApplication
from imagecolorpicker.controller import Controller

if __name__ == '__main__':
    controller: Controller = Controller()
    controller.startApplication()
    QApplication.exit(0)
