from typing import *
from PyQt6 import QtGui
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.uic import loadUi
from sys import argv
from os.path import (
    join,
    dirname,
)
from imagecolorpicker.colorgradient import DefaultGradient, ColorGradient, GradientMix, GradientWeight
from imagecolorpicker.gradientmodel import GradientModel
from glm import vec3

class GradientEditor(QWidget):
    UIFile = "gradienteditor.ui"

    def __init__(
        self: Self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Widget,
    ) -> None:
        super().__init__(parent, flags)

        loadUi(join(dirname(__file__), GradientEditor.UIFile), self)

        self._gradient: ColorGradient = DefaultGradient
        self._allColorMaps: List[Tuple[GradientWeight, GradientMix, List[vec3]]] = self._gradient.allColorMaps()
        self._gradientModel = GradientModel()
        self.tableView.setModel(self._gradientModel)
        self._gradientModel.load(self._allColorMaps, self._gradient)
        self.tableView.resizeColumnsToContents()
