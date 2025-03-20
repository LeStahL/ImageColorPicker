# from typing import *
# from PyQt6.QtCore import *
# from PyQt6.QtWidgets import *
# from PyQt6.QtGui import *
# from PyQt6.uic import loadUi
# from os.path import (
#     join,
#     dirname,
# )
from sys import exit
from imagecolorpicker.colorgradient import *
# from imagecolorpicker.pickablecolorlabel import PickableColorLabel
from imagecolorpicker.representation import Representation
from imagecolorpicker.language import Language
# from imagecolorpicker.gradienteditor import GradientEditor
from Pylette import extract_colors
from tempfile import TemporaryDirectory
from pathlib import Path
import rtoml
from enum import (
    IntEnum,
    auto,
)
from importlib.resources import files
from pathlib import Path
import imagecolorpicker
from .ui_mainwindow import Ui_MainWindow
from PyQt6.QtCore import (
    pyqtSignal,
    Qt,
)
from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
)
from PyQt6.QtGui import (
    QIcon,
)


class CoordinateType(IntEnum):
    AspectCorrectedBottomUp = auto()
    NormalizedBottomUp = auto()
    NormalizedTopDown = auto()


class MainWindow(QMainWindow):
    quitRequested: pyqtSignal = pyqtSignal()

    UIFile = "mainwindow.ui"
    
    def __init__(
        self: Self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.setWindowIcon(QIcon(str(files(imagecolorpicker) / 'team210.ico')))

    #     self.toolBar: QToolBar

    #     self.coordinateLabel = QLabel(self)
    #     self.coordinateLabel.setText("Coordinates: ")
    #     self.toolBar.addWidget(self.coordinateLabel)

    #     self.coordinateDropdown = QComboBox(self)
    #     for coordinateType in CoordinateType:
    #         self.coordinateDropdown.addItem(coordinateType.name, coordinateType)
    #     self.toolBar.addWidget(self.coordinateDropdown)

    #     self.picker: PickableColorLabel
    #     self.picker.hovered.connect(lambda cursor: self.statusBar().showMessage('Position: x = {}, y = {}'.format(*self._coordinates(cursor.x(), cursor.y()))))
    #     self.picker.picked.connect(self._updatePickInformation)
    #     self.actionOpen.triggered.connect(self.open)
    #     self.actionQuit.triggered.connect(self.quit)
    #     self.actionCopy.triggered.connect(self.copy)
    #     self.actionPaste.triggered.connect(self.paste)
    #     self.actionAbout.triggered.connect(self.about)
    #     self.actionExport_Palette.triggered.connect(self.exportPalette)
    #     self.actionImport_Palette.triggered.connect(self.importPalette)
    #     self.gradientEditor: GradientEditor
    #     self.gradientEditor.doubleClicked.connect(self.updateGradientViewWithColor)

    #     self.degreeLabel = QLabel(self.toolBar)
    #     self.degreeLabel.setText("Degree: ")
    #     self.toolBar.addWidget(self.degreeLabel)

    #     self.polynomialDegreeSpinBox = QSpinBox(self)
    #     self.polynomialDegreeSpinBox.setMinimum(1)
    #     self.polynomialDegreeSpinBox.setMaximum(7)
    #     self.polynomialDegreeSpinBox.setValue(6)
    #     self.polynomialDegreeSpinBox.valueChanged.connect(self.degreeChanged)
    #     self.polynomialDegreeSpinBox.setMinimumWidth(100)
    #     self.toolBar.addWidget(self.polynomialDegreeSpinBox)

    #     self.colorCountLabel = QLabel(self)
    #     self.colorCountLabel.setText("Count: ")
    #     self.toolBar.addWidget(self.colorCountLabel)

    #     self.colorCountSpinBox = QSpinBox(self)
    #     self.colorCountSpinBox.setMinimum(3)
    #     self.colorCountSpinBox.setMaximum(64)
    #     self.colorCountSpinBox.setValue(8)
    #     self.colorCountSpinBox.valueChanged.connect(self.colorCountChanged)
    #     self.colorCountSpinBox.setMinimumWidth(100)
    #     self.toolBar.addWidget(self.colorCountSpinBox)
    
    #     self.slugLabel = QLabel(self)
    #     self.slugLabel.setText("Slug: ")
    #     self.toolBar.addWidget(self.slugLabel)

    #     self.slugLineEdit = QLineEdit(self)
    #     self.slugLineEdit.setMaximumWidth(100)
    #     self.slugLineEdit.setMinimumWidth(100)
    #     self.slugLineEdit.setText("_example")
    #     self.toolBar.addWidget(self.slugLineEdit)

    #     self.languageLabel = QLabel(self)
    #     self.languageLabel.setText("Language: ")
    #     self.toolBar.addWidget(self.languageLabel)

    #     self.languageDropDown = QComboBox(self)
    #     for language in Language:
    #         self.languageDropDown.addItem(language.name, language)
    #     self.toolBar.addWidget(self.languageDropDown)

    #     self.languageLabel = QLabel(self)
    #     self.languageLabel.setText("Representation: ")
    #     self.toolBar.addWidget(self.languageLabel)

    #     self.representationDropDown = QComboBox(self)
    #     for representation in Representation:
    #         self.representationDropDown.addItem(representation.name, representation)
    #     self.toolBar.addWidget(self.representationDropDown)

    #     self.languageLabel = QLabel(self)
    #     self.languageLabel.setText("Weigh: ")
    #     self.toolBar.addWidget(self.languageLabel)

    #     self.weightDropDown = QComboBox(self)
    #     for weight in GradientWeight:
    #         self.weightDropDown.addItem(weight.name, weight)
    #     self.toolBar.addWidget(self.weightDropDown)

    #     self.languageLabel = QLabel(self)
    #     self.languageLabel.setText("Mix: ")
    #     self.toolBar.addWidget(self.languageLabel)

    #     self.mixDropDown = QComboBox(self)
    #     for mix in GradientMix:
    #         self.mixDropDown.addItem(mix.name, mix)
    #     self.toolBar.addWidget(self.mixDropDown)

    #     self.colorLabel: QLabel

    #     self.actionExtract_Palette: QAction
    #     self.actionExtract_Palette.triggered.connect(self.extractPalette)

    #     self.actionForce_16_9_View: QAction
    #     self.actionForce_16_9_View.triggered.connect(self._force16_9View)

    # def _force16_9View(self: Self) -> None:
    #     w = self.picker.width()
    #     h = int(9. / 16. * w)
    #     self.picker.resize(w, h)

    # def extractPalette(self: Self) -> None:
    #     with TemporaryDirectory() as directory:
    #         imagePath: Path = Path(directory) / 'image.jpg'
    #         self.picker._image.save(str(imagePath))
    #         palette = extract_colors(
    #             image=str(Path(directory) / 'image.jpg'),
    #             palette_size=int(self.colorCountSpinBox.value()),
    #             resize=False,
    #             # mode='MC',
    #             mode='KM',
    #             sort_mode='luminance',
    #         )
    #         palette = list(map(
    #             lambda color: QColor.fromRgb(*color.rgb),
    #             palette,
    #         ))
    #         palette = list(sorted(palette, key=lambda color: color.hue()))
    #         for colorIndex in range(int(self.colorCountSpinBox.value())):
    #             index = self.gradientEditor._gradientModel.index(colorIndex, 0)
    #             self.gradientEditor._gradientModel.setData(index, palette[colorIndex])
    #             self.gradientEditor._gradient = index.model()._gradient
    #             self.gradientEditor._allColorMaps = index.model()._allColorMaps
    #             self.gradientEditor.gradientPreview.changeColorMaps(index.model()._allColorMaps)

    # def _coordinates(self: Self, qtX: float, qtY: float) -> tuple[float, float]:
    #     if self.coordinateDropdown.currentData() == CoordinateType.NormalizedTopDown:
    #         return qtX, qtY
    #     qtY = 1. - qtY
    #     if self.coordinateDropdown.currentData() == CoordinateType.NormalizedBottomUp:
    #         return qtX, qtY
    #     width: int = self.picker.rect().width()
    #     height: int = self.picker.rect().height()
    #     return (qtX - .5) * width / height, (qtY - .5) * height / height

    # def degreeChanged(self: Self, value: int) -> None:
    #     ColorGradient.Degree = value
    #     self.gradientEditor._gradientModel.reload()
        
    # def colorCountChanged(self: Self, value: int) -> None:
    #     self.gradientEditor._gradientModel.setColorCount(value)

    # def representationChanged(self: Self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: List[Qt.ItemDataRole]) -> None:
    #     if Qt.ItemDataRole.EditRole in roles:
    #         self.colorLabel.setStyleSheet('background-color:{}'.format(topLeft.model()._color.name()))

    # def _updatePickInformation(self: Self, cursor: QPointF, color: QColor) -> None:
    #     self.colorLabel.setStyleSheet('background-color:{}'.format(color.name()))

    # def open(self: Self) -> None:
    #     filename, _ = QFileDialog.getOpenFileName(
    #         None,
    #         'Open image...',
    #         QDir.homePath(),
    #         'All Files (*.*)',
    #     )

    #     if filename == "":
    #         return
        
    #     self.picker.setImage(QImage(filename))
    #     self.setWindowTitle('Image Color Picker by Team210 - {}'.format(filename))

    # def quit(self: Self) -> None:
    #     exit(0)

    # def copy(self: Self) -> None:
    #     clipboard = QGuiApplication.clipboard()
    #     currentLanguage: Language = self.languageDropDown.currentData()
    #     currentRepresentation: Representation = self.representationDropDown.currentData()
    #     if currentLanguage == Language.GLSL:
    #         if currentRepresentation == Representation.ColorMap:
    #             clipboard.setText(self.gradientEditor._gradient.buildColorMap(self.weightDropDown.currentData(), self.mixDropDown.currentData()))
    #         elif currentRepresentation == Representation.Picked3ComponentColor:
    #             clipboard.setText('vec3({:.2f}, {:.2f}, {:.2f})'.format(*self.picker.components))
    #         elif currentRepresentation == Representation.Picked4ComponentColor:
    #             clipboard.setText('vec4({:.2f}, {:.2f}, {:.2f}, 1)'.format(*self.picker.components))
    #         elif currentRepresentation == Representation.PickedNearestGradientWeight:
    #             for weight, mix, colorMap in self.gradientEditor._allColorMaps:
    #                 if weight == self.weightDropDown.currentData() and mix == self.mixDropDown.currentData():
    #                     clipboard.setText('{:.2f}'.format(self.gradientEditor._gradient.nearestWeightInColorMap(colorMap, vec3(*self.picker.components))))
    #         elif currentRepresentation == Representation.GradientColorArray:
    #             clipboard.setText('vec3[{}]({})'.format(
    #                 len(self.gradientEditor._gradient._colors),
    #                 ', '.join(map(
    #                     str,
    #                     self.gradientEditor._gradient._colors,
    #                 )),
    #             ))
    #         elif currentRepresentation == Representation.GradientWeightArray:
    #             weights = self.gradientEditor._gradient.determineWeights(self.weightDropDown.currentData())
    #             clipboard.setText('float[{}]({})'.format(
    #                 len(weights),
    #                 ', '.join(map(
    #                     lambda weight: '{:.2f}'.format(weight),
    #                     weights,
    #                 )),
    #             ))
    #     elif currentLanguage == Language.HLSL:
    #         if currentRepresentation == Representation.ColorMap:
    #             clipboard.setText(self.gradientEditor._gradient.buildColorMap(self.weightDropDown.currentData(), self.mixDropDown.currentData()).replace('vec3', 'float3'))
    #         elif currentRepresentation == Representation.Picked3ComponentColor:
    #             clipboard.setText('float3({:.2f}, {:.2f}, {:.2f})'.format(*self.picker.components))
    #         elif currentRepresentation == Representation.Picked4ComponentColor:
    #             clipboard.setText('float4({:.2f}, {:.2f}, {:.2f}, 1)'.format(*self.picker.components))
    #         elif currentRepresentation == Representation.PickedNearestGradientWeight:
    #             for weight, mix, colorMap in self.gradientEditor._allColorMaps:
    #                 if weight == self.weightDropDown.currentData() and mix == self.mixDropDown.currentData():
    #                     clipboard.setText('{:.2f}'.format(self.gradientEditor._gradient.nearestWeightInColorMap(colorMap, vec3(*self.picker.components))))
    #         elif currentRepresentation == Representation.GradientColorArray:
    #             clipboard.setText('{{{}}}'.format(
    #                 ', '.join(map(
    #                     lambda color: ', '.join(map(lambda component: '{:.2f}'.format(component), color._color.to_tuple())),
    #                     self.gradientEditor._gradient._colors,
    #                 )),
    #             ))
    #         elif currentRepresentation == Representation.GradientWeightArray:
    #             weights = self.gradientEditor._gradient.determineWeights(self.weightDropDown.currentData())
    #             clipboard.setText('{{{}}}'.format(
    #                 ', '.join(map(
    #                     lambda weight: '{:.2f}'.format(weight),
    #                     weights,
    #                 )),
    #             ))
    #     elif currentLanguage == Language.CSS:
    #         if currentRepresentation == Representation.ColorMap:
    #             clipboard.setText(self.gradientEditor._gradient.buildCSSGradient(self.weightDropDown.currentData(), self.mixDropDown.currentData()))
    #         elif currentRepresentation == Representation.Picked3ComponentColor:
    #             clipboard.setText(self.picker._color.name())
    #     elif currentLanguage == Language.SVG:
    #         if currentRepresentation == Representation.ColorMap:
    #             clipboard.setText(self.gradientEditor._gradient.buildSVGGradient(self.weightDropDown.currentData(), self.mixDropDown.currentData()))
    #         elif currentRepresentation == Representation.Picked3ComponentColor:
    #             clipboard.setText(self.picker._color.name())
    #     elif currentLanguage == Language.PythonBytes:
    #         if currentRepresentation == Representation.ColorMap:
    #             clipboard.setText(self.gradientEditor._gradient.buildPythonBinary(self.weightDropDown.currentData(), self.mixDropDown.currentData()))

    # def paste(self: Self) -> None:
    #     clipboard = QGuiApplication.clipboard()

    #     if clipboard.mimeData().hasImage():
    #         self.picker.setImage(clipboard.image())
    #     if clipboard.mimeData().hasHtml():
    #         self.picker.loadFromHTML(clipboard.mimeData().html())
    #     if clipboard.mimeData().hasUrls():
    #         if len(clipboard.mimeData().urls()) == 0:
    #             return

    #         # Only load first URL.
    #         url: QUrl = clipboard.mimeData().urls()[0]
    #         self.picker.loadFromUrl(url)

    # def about(self: Self) -> None:
    #     aboutMessage = QMessageBox()
    #     aboutMessage.setWindowIcon(QIcon(join(dirname(__file__), MainWindow.IconFile)))
    #     aboutMessage.setText("Image Color Picker is GPLv3 and (c) 2023 Alexander Kraus <nr4@z10.info>.")
    #     aboutMessage.setWindowTitle("About Image Color Picker")
    #     aboutMessage.setIcon(QMessageBox.Icon.Information)
    #     aboutMessage.exec()

    # def updateGradientViewWithColor(self: Self, index: QModelIndex) -> None:
    #     index.model().setData(index, self.picker._color, Qt.ItemDataRole.EditRole)
    #     self.gradientEditor._gradient = index.model()._gradient
    #     self.gradientEditor._allColorMaps = index.model()._allColorMaps
    #     self.gradientEditor.gradientPreview.changeColorMaps(index.model()._allColorMaps)

    # def exportPalette(self: Self) -> None:
    #     settings = QSettings()
    #     filename, _ = QFileDialog.getSaveFileName(
    #         None,
    #         'Save palette...',
    #         settings.value("save_palette_path", QDir.homePath()),
    #         "All Supported Files (*.toml);;TOML project files (*.toml)",
    #     )

    #     if filename == "":
    #         return

    #     if len(Path(filename).suffixes) == 0:
    #         filename += '.toml'

    #     file_info = QFileInfo(filename)
    #     settings.setValue("save_palette_path", file_info.absoluteDir().absolutePath())
    #     suffix: str = Path(filename).suffix
        
    #     if suffix == '.toml':
    #         Path(filename).write_text(rtoml.dumps({
    #             'palette': {
    #                 'name': self.slugLineEdit.text(),
    #                 'colors': list(map(
    #                     lambda color: color.toList(),
    #                     self.gradientEditor._gradient._colors,
    #                 )),
    #             },
    #         }, pretty=True))

    # def importPalette(self: Self) -> None:
    #     settings = QSettings()
    #     filename, _ = QFileDialog.getOpenFileName(
    #         None,
    #         'Load palette...',
    #         settings.value("load_palette_path", QDir.homePath()),
    #         "All Supported Files (*.toml);;TOML project files (*.toml)",
    #     )

    #     if filename == "":
    #         return

    #     if len(Path(filename).suffixes) == 0:
    #         filename += '.toml'

    #     file_info = QFileInfo(filename)
    #     settings.setValue("load_palette_path", file_info.absoluteDir().absolutePath())
    #     suffix: str = Path(filename).suffix
        
    #     if suffix == '.toml':
    #         paletteObject: Dict = rtoml.loads(Path(filename).read_text())
    #         self.colorCountSpinBox.setValue(len(paletteObject['palette']['colors']))
    #         gradient: ColorGradient = ColorGradient(*tuple(map(
    #             lambda colorList: Color(*colorList),
    #             paletteObject['palette']['colors'],
    #         )))
    #         allColorMaps: List[Tuple[GradientWeight, GradientMix, List[vec3]]] = gradient.allColorMaps()
    #         self.gradientEditor._gradientModel.load(allColorMaps, gradient)
    #         self.gradientEditor._gradient = gradient
    #         self.gradientEditor._allColorMaps = allColorMaps
    #         self.gradientEditor._gradientModel.reload()
    #         self.gradientEditor.gradientPreview.changeColorMaps(allColorMaps)
    #         self.update()