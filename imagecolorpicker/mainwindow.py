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
from imagecolorpicker.pickablecolorlabel import PickableColorLabel
from imagecolorpicker.representation import Representation
from imagecolorpicker.language import Language
from imagecolorpicker.gradienteditor import GradientEditor


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

        self.picker: PickableColorLabel
        self.picker.hovered.connect(lambda cursor: self.statusBar().showMessage('Position: x = {}, y = {}'.format(cursor.x(), cursor.y())))
        self.picker.picked.connect(self._updatePickInformation)
        self.actionOpen.triggered.connect(self.open)
        self.actionQuit.triggered.connect(self.quit)
        self.actionCopy.triggered.connect(self.copy)
        self.actionPaste.triggered.connect(self.paste)
        self.actionAbout.triggered.connect(self.about)
        self.gradientEditor: GradientEditor
        self.gradientEditor.doubleClicked.connect(self.updateGradientViewWithColor)

        self.toolBar: QToolBar
        self.degreeLabel = QLabel(self.toolBar)
        self.degreeLabel.setText("Degree: ")
        self.toolBar.addWidget(self.degreeLabel)

        self.polynomialDegreeSpinBox = QSpinBox(self)
        self.polynomialDegreeSpinBox.setMinimum(1)
        self.polynomialDegreeSpinBox.setMaximum(7)
        self.polynomialDegreeSpinBox.setValue(6)
        self.polynomialDegreeSpinBox.valueChanged.connect(self.degreeChanged)
        self.polynomialDegreeSpinBox.setMinimumWidth(100)
        self.toolBar.addWidget(self.polynomialDegreeSpinBox)

        self.colorCountLabel = QLabel(self)
        self.colorCountLabel.setText("Count: ")
        self.toolBar.addWidget(self.colorCountLabel)

        self.colorCountSpinBox = QSpinBox(self)
        self.colorCountSpinBox.setMinimum(3)
        self.colorCountSpinBox.setMaximum(15)
        self.colorCountSpinBox.setValue(8)
        self.colorCountSpinBox.valueChanged.connect(self.colorCountChanged)
        self.colorCountSpinBox.setMinimumWidth(100)
        self.toolBar.addWidget(self.colorCountSpinBox)
    
        self.slugLabel = QLabel(self)
        self.slugLabel.setText("Slug: ")
        self.toolBar.addWidget(self.slugLabel)

        self.slugLineEdit = QLineEdit(self)
        self.slugLineEdit.setMaximumWidth(100)
        self.slugLineEdit.setMinimumWidth(100)
        self.slugLineEdit.setText("_example")
        self.toolBar.addWidget(self.slugLineEdit)

        self.languageLabel = QLabel(self)
        self.languageLabel.setText("Language: ")
        self.toolBar.addWidget(self.languageLabel)

        self.languageDropDown = QComboBox(self)
        for language in Language:
            self.languageDropDown.addItem(language.name, language)
        self.toolBar.addWidget(self.languageDropDown)

        self.languageLabel = QLabel(self)
        self.languageLabel.setText("Representation: ")
        self.toolBar.addWidget(self.languageLabel)

        self.representationDropDown = QComboBox(self)
        for representation in Representation:
            self.representationDropDown.addItem(representation.name, representation)
        self.toolBar.addWidget(self.representationDropDown)

        self.languageLabel = QLabel(self)
        self.languageLabel.setText("Weigh: ")
        self.toolBar.addWidget(self.languageLabel)

        self.weightDropDown = QComboBox(self)
        for weight in GradientWeight:
            self.weightDropDown.addItem(weight.name, weight)
        self.toolBar.addWidget(self.weightDropDown)

        self.languageLabel = QLabel(self)
        self.languageLabel.setText("Mix: ")
        self.toolBar.addWidget(self.languageLabel)

        self.mixDropDown = QComboBox(self)
        for mix in GradientMix:
            self.mixDropDown.addItem(mix.name, mix)
        self.toolBar.addWidget(self.mixDropDown)

        self.colorLabel: QLabel

    def degreeChanged(self: Self, value: int) -> None:
        ColorGradient.Degree = value
        self.gradientEditor._gradientModel.reload()
        
    def colorCountChanged(self: Self, value: int) -> None:
        self.gradientEditor._gradientModel.setColorCount(value)

    def representationChanged(self: Self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[Qt.ItemDataRole]) -> None:
        if Qt.ItemDataRole.EditRole in roles:
            self.colorLabel.setStyleSheet('background-color:{}'.format(topLeft.model()._color.name()))

    def _updatePickInformation(self: Self, cursor: QPointF, color: QColor) -> None:
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

        match self.languageDropDown.currentData():
            case Language.GLSL:
                match self.representationDropDown.currentData():
                    case Representation.ColorMap:
                        clipboard.setText(self.gradientEditor._gradient.buildColorMap(self.weightDropDown.currentData(), self.mixDropDown.currentData()))
                    case Representation.Picked3ComponentColor:
                        clipboard.setText('vec3({:.2f}, {:.2f}, {:.2f})'.format(*self.picker.components))
                    case Representation.Picked4ComponentColor:
                        clipboard.setText('vec4({:.2f}, {:.2f}, {:.2f}, 1)'.format(*self.picker.components))
                    case Representation.PickedNearestGradientWeight:
                        for weight, mix, colorMap in self.gradientEditor._allColorMaps:
                            if weight == self.weightDropDown.currentData() and mix == self.mixDropDown.currentData():
                                clipboard.setText('{:.2f}'.format(self.gradientEditor._gradient.nearestWeightInColorMap(colorMap, vec3(*self.picker.components))))
                    case Representation.GradientColorArray:
                        clipboard.setText('vec3[{}]({})'.format(
                            len(self.gradientEditor._gradient._colors),
                            ', '.join(map(
                                str,
                                self.gradientEditor._gradient._colors,
                            )),
                        ))
                    case Representation.GradientWeightArray:
                        weights = self.gradientEditor._gradient.determineWeights(self.weightDropDown.currentData())
                        clipboard.setText('float[{}]({})'.format(
                            len(weights),
                            ', '.join(map(
                                lambda weight: '{:.2f}'.format(weight),
                                weights,
                            )),
                        ))
            case Language.HLSL:
                match self.representationDropDown.currentData():
                    case Representation.ColorMap:
                        clipboard.setText(self.gradientEditor._gradient.buildColorMap(self.weightDropDown.currentData(), self.mixDropDown.currentData()).replace('vec3', 'float3'))
                    case Representation.Picked3ComponentColor:
                        clipboard.setText('float3({:.2f}, {:.2f}, {:.2f})'.format(*self.picker.components))
                    case Representation.Picked4ComponentColor:
                        clipboard.setText('float4({:.2f}, {:.2f}, {:.2f}, 1)'.format(*self.picker.components))
                    case Representation.PickedNearestGradientWeight:
                        for weight, mix, colorMap in self.gradientEditor._allColorMaps:
                            if weight == self.weightDropDown.currentData() and mix == self.mixDropDown.currentData():
                                clipboard.setText('{:.2f}'.format(self.gradientEditor._gradient.nearestWeightInColorMap(colorMap, vec3(*self.picker.components))))
                    case Representation.GradientColorArray:
                        clipboard.setText('{{{}}}'.format(
                            ', '.join(map(
                                lambda color: ', '.join(map(lambda component: '{:.2f}'.format(component), color._color.to_tuple())),
                                self.gradientEditor._gradient._colors,
                            )),
                        ))
                    case Representation.GradientWeightArray:
                        weights = self.gradientEditor._gradient.determineWeights(self.weightDropDown.currentData())
                        clipboard.setText('{{{}}}'.format(
                            ', '.join(map(
                                lambda weight: '{:.2f}'.format(weight),
                                weights,
                            )),
                        ))
            case Language.CSS:
                match self.representationDropDown.currentData():
                    case Representation.ColorMap:
                        clipboard.setText(self.gradientEditor._gradient.buildCSSGradient(self.weightDropDown.currentData(), self.mixDropDown.currentData()))
                    case Representation.Picked3ComponentColor:
                        clipboard.setText(self.picker._color.name())
            case Language.SVG:
                match self.representationDropDown.currentData():
                    case Representation.ColorMap:
                        clipboard.setText(self.gradientEditor._gradient.buildSVGGradient(self.weightDropDown.currentData(), self.mixDropDown.currentData()))
                    case Representation.Picked3ComponentColor:
                        clipboard.setText(self.picker._color.name()) 

    def paste(self: Self) -> None:
        clipboard = QGuiApplication.clipboard()

        if clipboard.mimeData().hasImage():
            self.picker.setImage(clipboard.image())
        if clipboard.mimeData().hasHtml():
            self.picker.loadFromHTML(clipboard.mimeData().html())
        if clipboard.mimeData().hasUrls():
            if len(clipboard.mimeData().urls()) == 0:
                return

            # Only load first URL.
            url: QUrl = clipboard.mimeData().urls()[0]
            self.picker.loadFromUrl(url)

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
