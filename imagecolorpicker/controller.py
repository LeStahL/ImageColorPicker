from typing import (
    Self,
    Optional,
)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import (
    QIcon,
    QColor,
)
from PyQt6.QtCore import (
    QModelIndex,
    Qt,
    QPoint,
    QPointF,
)
from sys import argv
from pathlib import Path
from importlib.resources import files
import imagecolorpicker
from imagecolorpicker.widgets.mainwindow.mainwindow import MainWindow


class Controller:
    def __init__(
        self: Self,
    ) -> None:
        QApplication.setOrganizationName("Team210 Demoscene Productions")
        QApplication.setApplicationName("ImageColorPicker")
        QApplication.setWindowIcon(QIcon(str(files(imagecolorpicker) / 'team210.ico')))

        self._mainWindow: MainWindow = MainWindow()
        self._mainWindow.quitRequested.connect(lambda: QApplication.exit(0))
        self._mainWindow.show()

    def startApplication(
        self: Self,
    ) -> None:
        QApplication.exec()
