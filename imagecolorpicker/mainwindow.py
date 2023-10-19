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

    def _updatePickInformation(self: Self, cursor: QPointF, color: QColor) -> None:
        floatArgs = color.redF(), color.greenF(), color.blueF()
        intArgs = color.red(), color.green(), color.blue()
        self.vec3LineEdit.setText('vec3({:.2f}, {:.2f}, {:.2f})'.format(*floatArgs))
        self.vec4LineEdit.setText('vec4({:.2f}, {:.2f}, {:.2f}, 1.)'.format(*floatArgs))
        self.float3LineEdit.setText('{{{:.2f}f, {:.2f}f, {:.2f}f}}'.format(*floatArgs))
        self.float4LineEdit.setText('{{{:.2f}f, {:.2f}f, {:.2f}f, 1.0f}}'.format(*floatArgs))
        self.hexLineEdit.setText(color.name())
        self.qColorLineEdit.setText('QColor({}, {}, {})'.format(*intArgs))
        self.listIntLineEdit.setText('[{}, {}, {}]'.format(*intArgs))
        self.listFloatLineEdit.setText('[{:.2f}, {:.2f}, {:.2f}]'.format(*floatArgs))
        self.colorTLineEdit.setText('{{{:.2f}, {:.2f}, {:.2f}}}'.format(*floatArgs))
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
        if self.copyComboBox.currentIndex() == 0:
            clipboard.setText(self.vec3LineEdit.text())
        if self.copyComboBox.currentIndex() == 1:
            clipboard.setText(self.vec4LineEdit.text())
        if self.copyComboBox.currentIndex() == 2:
            clipboard.setText(self.float3LineEdit.text())
        if self.copyComboBox.currentIndex() == 3:
            clipboard.setText(self.float4LineEdit.text())
        if self.copyComboBox.currentIndex() == 4:
            clipboard.setText(self.hexLineEdit.text())
        if self.copyComboBox.currentIndex() == 5:
            clipboard.setText(self.qColorLineEdit.text())
        if self.copyComboBox.currentIndex() == 6:
            clipboard.setText(self.listIntLineEdit.text())
        if self.copyComboBox.currentIndex() == 7:
            clipboard.setText(self.listFloatLineEdit.text())
        if self.copyComboBox.currentIndex() == 8:
            clipboard.setText(self.colorTLineEdit.text())
        
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
