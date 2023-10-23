from typing import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.uic import loadUi
from os.path import (
    join,
    dirname,
)
from sys import exit
from imagecolorpicker.colorgradient import *
from imagecolorpicker.codemodel import *

class MainWindow(QMainWindow):
    UIFile = "mainwindow.ui"
    IconFile = "team210.ico"
    
    def __init__(
        self: Self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)

        loadUi(join(dirname(__file__), MainWindow.UIFile), self)
        self.setWindowIcon(QIcon(join(dirname(__file__), MainWindow.IconFile)))

        self.picker.hovered.connect(lambda cursor: self.statusBar().showMessage('Position: x = {}, y = {}'.format(cursor.x(), cursor.y())))
        self.picker.picked.connect(self._updatePickInformation)
        self.actionOpen.triggered.connect(self.open)
        self.actionQuit.triggered.connect(self.quit)
        self.actionCopy.triggered.connect(self.copy)
        self.actionPaste.triggered.connect(self.paste)
        self.actionAbout.triggered.connect(self.about)
        self.gradientEditor.doubleClicked.connect(self.updateGradientViewWithColor)

        self._codeModel = CodeModel()
        self._codeModel.dataChanged.connect(self.representationChanged)
        self.codeView.setModel(self._codeModel)
        self.codeView.resizeColumnsToContents()

        self.degreeLabel = QLabel(self.toolBar)
        self.degreeLabel.setText("Degree: ")
        self.toolBar.addWidget(self.degreeLabel)

        self.polynomialDegreeSpinBox = QSpinBox(self)
        self.polynomialDegreeSpinBox.setMinimum(1)
        self.polynomialDegreeSpinBox.setMaximum(7)
        self.polynomialDegreeSpinBox.setValue(6)
        self.polynomialDegreeSpinBox.valueChanged.connect(self.degreeChanged)
        self.toolBar.addWidget(self.polynomialDegreeSpinBox)

        self.colorCountLabel = QLabel(self)
        self.colorCountLabel.setText("Count: ")
        self.toolBar.addWidget(self.colorCountLabel)

        self.colorCountSpinBox = QSpinBox(self)
        self.colorCountSpinBox.setMinimum(3)
        self.colorCountSpinBox.setMaximum(15)
        self.colorCountSpinBox.setValue(8)
        self.colorCountSpinBox.valueChanged.connect(self.colorCountChanged)
        self.toolBar.addWidget(self.colorCountSpinBox)
    
    def degreeChanged(self: Self, value: int) -> None:
        ColorGradient.Degree = value
        self.gradientEditor._gradientModel.reload()
        
    def colorCountChanged(self: Self, value: int) -> None:
        self.gradientEditor._gradientModel.setColorCount(value)

    def representationChanged(self: Self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[Qt.ItemDataRole]) -> None:
        if Qt.ItemDataRole.EditRole in roles:
            self.colorLabel.setStyleSheet('background-color:{}'.format(topLeft.model()._color.name()))

    def _updatePickInformation(self: Self, cursor: QPointF, color: QColor) -> None:
        self._codeModel.load(color)
        self.colorLabel.setStyleSheet('background-color:{}'.format(color.name()))

    def open(self: Self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            None,
            'Open image...',
            QDir.homePath(),
            'All Files (*.*)',
        )

        if filename == "":
            return
        
        self.picker.setImage(QImage(filename))
        self.setWindowTitle('Image Color Picker by Team210 - {}'.format(filename))

    def quit(self: Self) -> None:
        exit(0)

    def copy(self: Self) -> None:
        clipboard = QGuiApplication.clipboard()
        
        # Single color entries
        if self.copyComboBox.currentIndex() <= 8:
            clipboard.setText(self._codeModel.data(self._codeModel.index(self.copyComboBox.currentIndex(), 2)))

        # Gradient entries
        if self.copyComboBox.currentIndex() == 9:
            clipboard.setText(self.gradientEditor._gradient.buildColorMap(GradientWeight.Unweighted, GradientMix.Oklab))
        if self.copyComboBox.currentIndex() == 10:
            clipboard.setText(self.gradientEditor._gradient.buildColorMap(GradientWeight.Unweighted, GradientMix.RGB))
        if self.copyComboBox.currentIndex() == 11:
            clipboard.setText(self.gradientEditor._gradient.buildColorMap(GradientWeight.RGB, GradientMix.Oklab))
        if self.copyComboBox.currentIndex() == 12:
            clipboard.setText(self.gradientEditor._gradient.buildColorMap(GradientWeight.RGB, GradientMix.RGB))
        if self.copyComboBox.currentIndex() == 13:
            clipboard.setText(self.gradientEditor._gradient.buildColorMap(GradientWeight.Oklab, GradientMix.Oklab))
        if self.copyComboBox.currentIndex() == 14:
            clipboard.setText(self.gradientEditor._gradient.buildColorMap(GradientWeight.Oklab, GradientMix.RGB))

    def paste(self: Self) -> None:
        clipboard = QGuiApplication.clipboard()

        if clipboard.mimeData().hasImage():
            self.picker.setImage(clipboard.image())
        if clipboard.mimeData().hasHtml():
            self.picker.loadFromHTML(clipboard.mimeData().html())

    def about(self: Self) -> None:
        aboutMessage = QMessageBox()
        aboutMessage.setWindowIcon(QIcon(join(dirname(__file__), MainWindow.IconFile)))
        aboutMessage.setText("Image Color Picker is GPLv3 and (c) 2023 Alexander Kraus <nr4@z10.info>.")
        aboutMessage.setWindowTitle("About Image Color Picker")
        aboutMessage.setIcon(QMessageBox.Icon.Information)
        aboutMessage.exec()

    def updateGradientViewWithColor(self: Self, index: QModelIndex) -> None:
        index.model().setData(index, self.picker._color, Qt.ItemDataRole.EditRole)
        self.gradientEditor._gradient = index.model()._gradient
        self.gradientEditor._allColorMaps = index.model()._allColorMaps
        self.gradientEditor.gradientPreview.changeColorMaps(index.model()._allColorMaps)
