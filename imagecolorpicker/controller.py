from typing import (
    Self,
    Optional,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMenu,
)
from PyQt6.QtGui import (
    QIcon,
    QColor,
    QImage,
    QAction,
    QGuiApplication,
)
from PyQt6.QtCore import (
    QModelIndex,
    Qt,
    QPoint,
    QPointF,
    QDir,
    QFileInfo,
    QSettings,
)
from sys import argv
from pathlib import Path
from importlib.resources import files
import imagecolorpicker
from .widgets.mainwindow.mainwindow import MainWindow
from .widgets.pickablecolorlabel.pickablecolorlabel import PickableColorLabel
from .cmapfile import CMapFile
from .colorgradient import (
    DefaultGradient1,
    DefaultGradient2,
)
from .model.gradientlistmodel import (
    GradientListModel,
)
from .delegate.gradientlistdelegate import GradientListDelegate
from .widgets import pickablecolorlabel
from .model.imagelistmodel import ImageListModel
from .delegate.imagelistdelegate import ImageListDelegate
from .colorgradient import ColorGradient
from .model.gradientpropertymodel import GradientPropertyModel
from .delegate.gradientpropertydelegate import GradientPropertyDelegate
from .model.gradientpropertyrowtype import GradientPropertyRowType
from .model.gradientpropertycolumntype import GradientPropertyColumnType
from .widgets.gradientwidget import gradientwidget
from .model.gradientcolormodel import GradientColorModel
from .delegate.gradientcolordelegate import GradientColorDelegate
from copy import deepcopy
from glm import vec3
from uuid import uuid4
from .colorspace import ColorSpaceType, ColorSpace
from random import uniform
from tempfile import TemporaryDirectory
from Pylette import extract_colors
from rtoml import loads, dumps
from .language import Language
from .representation import Representation
from .model.settingsmodel import SettingsModel
from .delegate.settingsdelegate import SettingsDelegate
from .export import Export
from .optimizationmodel import OptimizationModel


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

        self._cmapFile: CMapFile = CMapFile(
            images=[
                QImage(str(files(pickablecolorlabel) / PickableColorLabel.DefaultImage)),
            ],
            gradients=[
                DefaultGradient1,
                DefaultGradient2,
            ],
        )

        self._gradientListModel: GradientListModel = GradientListModel()
        self._gradientListModel.currentGradientChanged.connect(self._currentGradientChanged)
        self._gradientListModel.dataChanged.connect(self._gradientListDataChanged)

        self._gradientListDelegate: GradientListDelegate = GradientListDelegate()        
        
        self._previewGradientListmodel: GradientListModel = GradientListModel()
        self._mainWindow._ui.gradientPreviewTableView.setModel(self._previewGradientListmodel)
        self._mainWindow._ui.gradientPreviewTableView.setItemDelegate(self._gradientListDelegate)

        self._mainWindow._ui.gradientTableView.setItemDelegate(self._gradientListDelegate)
        self._mainWindow._ui.gradientTableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._mainWindow._ui.gradientTableView.setModel(self._gradientListModel)
        self._mainWindow._ui.gradientTableView.customContextMenuRequested.connect(self._gradientListContextMenuRequested)

        self._imageListModel: ImageListModel = ImageListModel()

        self._imageListDelegate: ImageListDelegate = ImageListDelegate()

        self._mainWindow._ui.imageListView.setItemDelegate(self._imageListDelegate)
        self._mainWindow._ui.imageListView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._mainWindow._ui.imageListView.setModel(self._imageListModel)
        self._mainWindow._ui.imageListView.customContextMenuRequested.connect(self._imageListContextMenuRequested)
        
        self._gradientPropertyModel: GradientPropertyModel = GradientPropertyModel()
        self._gradientPropertyModel.dataChanged.connect(self._gradientPropertyChanged)

        self._gradientPropertyDelegate: GradientPropertyDelegate = GradientPropertyDelegate()

        self._mainWindow._ui.gradientPropertyTableView.setItemDelegate(self._gradientPropertyDelegate)
        self._mainWindow._ui.gradientPropertyTableView.setModel(self._gradientPropertyModel)

        self._gradientColorModel: GradientColorModel = GradientColorModel()
        self._gradientColorModel.dataChanged.connect(self._gradientColorDataChanged)

        self._gradientColorDelegate: GradientColorDelegate = GradientColorDelegate()

        self._mainWindow._ui.gradientColorTableView.setModel(self._gradientColorModel)
        self._mainWindow._ui.gradientColorTableView.setItemDelegate(self._gradientColorDelegate)
        self._mainWindow._ui.gradientColorTableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._mainWindow._ui.gradientColorTableView.customContextMenuRequested.connect(self._colorTableContextMenuRequested)

        self._mainWindow._ui.picker.imageChanged.connect(self._pickerImageChanged)

        self._mainWindow._ui.actionOpen.triggered.connect(self._openFile)
        self._mainWindow._ui.actionSave.triggered.connect(self._saveFile)

        self._mainWindow._ui.actionAdd_Gradient.triggered.connect(self._addGradient)
        self._mainWindow._ui.actionRemove_Current_Gradient.triggered.connect(self._removeCurrentGradient)

        self._mainWindow._ui.actionAdd_Color.triggered.connect(self._addColor)
        self._mainWindow._ui.actionRemove_Color.triggered.connect(self._removeColor)

        self._mainWindow._ui.actionExtract_Palette.triggered.connect(self.extractPalette)

        self._mainWindow._ui.actionImport_Palette.triggered.connect(self._importPalette)
        self._mainWindow._ui.actionExport_Palette.triggered.connect(self._exportPalette)

        self._mainWindow._ui.actionCopy.triggered.connect(self._copy)

        self.updateFromCmapFile()

        self._settingsModel: SettingsModel = SettingsModel()
        self._mainWindow._ui.settingsTableView.setModel(self._settingsModel)

        self._settingsDelegate: SettingsDelegate = SettingsDelegate()
        self._mainWindow._ui.settingsTableView.setItemDelegate(self._settingsDelegate)

        self._mainWindow.cmapPasted.connect(self._cmapPasted)

    def _copy(self: Self) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(Export.Export(self._settingsModel.language, self._settingsModel.representation, self._gradientListModel._gradientList[self._gradientListModel._currentIndex], self._gradientListModel._gradientList, vec3(*self._mainWindow._ui.picker.components)))

    def _exportPalette(self: Self) -> None:
        settings = QSettings()
        filename, _ = QFileDialog.getSaveFileName(
            None,
            'Save palette...',
            settings.value("save_palette_path", QDir.homePath()),
            "All Supported Files (*.toml);;TOML project files (*.toml)",
        )

        if filename == "":
            return

        if len(Path(filename).suffixes) == 0:
            filename += '.toml'

        file_info = QFileInfo(filename)
        settings.setValue("save_palette_path", file_info.absoluteDir().absolutePath())
        suffix: str = Path(filename).suffix
        
        if suffix == '.toml':
            Path(filename).write_text(dumps({
                'palette': {
                    'name': self._cmapFile._gradients[self._gradientListModel._currentIndex]._name,
                    'colors': list(map(
                        lambda color: [color.x, color.y, color.z],
                        self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors,
                    )),
                },
            }, pretty=True))

    def _importPalette(self: Self) -> None:
        settings = QSettings()
        filename, _ = QFileDialog.getOpenFileName(
            None,
            'Load palette...',
            settings.value("load_palette_path", QDir.homePath()),
            "All Supported Files (*.toml);;TOML project files (*.toml)",
        )

        if filename == "":
            return

        if len(Path(filename).suffixes) == 0:
            filename += '.toml'

        file_info = QFileInfo(filename)
        settings.setValue("load_palette_path", file_info.absoluteDir().absolutePath())
        suffix: str = Path(filename).suffix
        
        if suffix == '.toml':
            paletteObject: dict = loads(Path(filename).read_text())
            self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors = ColorSpace.SortByCIEH(list(map(
                lambda colorList: vec3(*colorList),
                paletteObject['palette']['colors'],
            )))
            index = self._gradientListModel._currentIndex
            self.updateFromCmapFile()
            self._gradientListModel.changeCurrent(index)

    def _removeColor(self: Self) -> None:
        if len(self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors) <= 1:
            return
        del self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors[-1]
        index = min(
            self._gradientListModel._currentIndex,
            len(self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors) - 1,
        )
        self.updateFromCmapFile()
        self._gradientListModel.changeCurrent(index)

    def _addColor(self: Self) -> None:
        self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors.append(vec3(1,1,1))
        index = self._gradientListModel._currentIndex
        self.updateFromCmapFile()
        self._gradientListModel.changeCurrent(index)

    def _addGradient(self: Self) -> None:
        self._cmapFile._gradients.append(ColorGradient(
            str(uuid4()),
            7,
            ColorSpaceType.CIELAB,
            ColorSpaceType.CIELAB,
            ColorSpace.SortByCIEH([
                vec3(uniform(0,.1), uniform(0,.1), uniform(0,.1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
                vec3(uniform(0,1), uniform(0,1), uniform(0,1)),
            ]),
        ))
        self.updateFromCmapFile()
        self._gradientListModel.changeCurrent(len(self._cmapFile._gradients) - 1)

    def _removeCurrentGradient(self: Self) -> None:
        del self._cmapFile._gradients[self._gradientListModel._currentIndex]
        self.updateFromCmapFile()

    def updateFromCmapFile(
        self: Self,
    ) -> None:
        self._gradientListModel.loadGradientList(self._cmapFile._gradients)
        self._imageListModel.loadImageList(self._cmapFile._images)
        self._updateGradientPreview()
        self._gradientPropertyModel.loadGradient(self._cmapFile._gradients[self._gradientListModel._currentIndex])
        self._gradientColorModel.loadGradient(self._cmapFile._gradients[self._gradientListModel._currentIndex])

    def _gradientListContextMenuRequested(self: Self, position: QPoint) -> None:
        index: QModelIndex = self._mainWindow._ui.gradientTableView.indexAt(position)
        if index.isValid():
            self._gradientListModel.changeCurrent(index.row())
        else:
            self._mainWindow._ui.menuGradient.move(self._mainWindow._ui.gradientTableView.mapToGlobal(position))
            self._mainWindow._ui.menuGradient.show()

    def _colorTableContextMenuRequested(self: Self, position: QPoint) -> None:
        index: QModelIndex = self._mainWindow._ui.gradientColorTableView.indexAt(position)
        if index.isValid():
            self._gradientColorModel.updateColor(index.row(), self._mainWindow._ui.picker._color)

    def _imageListContextMenuRequested(self: Self, position: QPoint) -> None:
        index: QModelIndex = self._mainWindow._ui.imageListView.indexAt(position)
        if index.isValid():
            self._imageListModel.changeCurrent(index.row())
            self._mainWindow._ui.picker.setImage(self._imageListModel._imageList[index.row()])

    def _updateGradientPreview(self: Self) -> None:
        previewGradientList: list[ColorGradient] = list(map(
            lambda colorspaces: self._gradientListModel.copyCurrentGradientWithColorSpaces(*colorspaces),
            self._cmapFile._previewColorSpaces,
        ))
        self._previewGradientListmodel.loadGradientList(previewGradientList)

    def _currentGradientChanged(self: Self, gradient: ColorGradient) -> None:
        self._gradientPropertyModel.loadGradient(gradient)
        self._gradientColorModel.loadGradient(gradient)

    def _gradientPropertyChanged(self: Self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: list[Qt.ItemDataRole]):
        if Qt.ItemDataRole.EditRole in roles:
            self._gradientListModel.updateCurrentGradient()
            self._updateGradientPreview()

    def _gradientListDataChanged(self: Self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: list[Qt.ItemDataRole]):
        if Qt.ItemDataRole.EditRole in roles: 
            index: QModelIndex = self._gradientPropertyModel.index(
                self._gradientPropertyModel._rowList.index(GradientPropertyRowType.Name),
                self._gradientPropertyModel._columnList.index(GradientPropertyColumnType.Value),
            )
            self._gradientPropertyModel.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
            self._updateGradientPreview()

    def _gradientColorDataChanged(self: Self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: list[Qt.ItemDataRole]):
        if Qt.ItemDataRole.EditRole in roles:
            self._gradientListModel.updateCurrentGradient()
            self._updateGradientPreview()

    def _pickerImageChanged(self: Self, image: QImage) -> None:
        self._cmapFile._images.append(image)
        self._imageListModel.loadImageList(self._cmapFile._images)

    def _openFile(self: Self) -> None:
        settings = QSettings()
        filename, _ = QFileDialog.getOpenFileName(
            None,
            'Open cmap...',
            settings.value("open_path", QDir.homePath()),
            'TOML Files (*.toml)',
        )

        if filename == "":
            return

        file_info = QFileInfo(filename)
        settings.setValue("open_path", file_info.absoluteDir().absolutePath())

        self._cmapFile.load(Path(filename))
        self.updateFromCmapFile()

    def _saveFile(self: Self) -> None:
        settings = QSettings()
        filename, _ = QFileDialog.getSaveFileName(
            None,
            'Save cmap...',
            settings.value("save_path", QDir.homePath()),
            'TOML Files (*.toml)',
        )

        if filename == "":
            return

        file_info = QFileInfo(filename)
        settings.setValue("save_path", file_info.absoluteDir().absolutePath())

        self._cmapFile.save(Path(filename))

    def extractPalette(self: Self) -> None:
        with TemporaryDirectory() as directory:
            imagePath: Path = Path(directory) / 'image.jpg'
            self._mainWindow._ui.picker._image.save(str(imagePath))
            palette = extract_colors(
                image=str(Path(directory) / 'image.jpg'),
                palette_size=len(self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors),
                resize=False,
                # mode='MC',
                mode='KM',
                sort_mode='luminance',
            )
            palette = list(map(
                lambda color: vec3(*color.rgb) / 255.,
                palette,
            ))
            palette = ColorSpace.SortByCIEH(palette)
            self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors = palette
            index = self._gradientListModel._currentIndex
            self.updateFromCmapFile()
            self._gradientListModel.changeCurrent(index)

    def _cmapPasted(self: Self, cmap: list[vec3]) -> None:
        print(cmap)
        colors = []
        for colorIndex in range(self._cmapFile._gradients[self._gradientListModel._currentIndex].colorCount):
            colors.append(vec3(
                OptimizationModel.Polynomial(
                    colorIndex / self._cmapFile._gradients[self._gradientListModel._currentIndex].colorCount,
                    *map(
                        lambda cmapEntry: cmapEntry.x,
                        cmap,
                    ),
                ),
                OptimizationModel.Polynomial(
                    colorIndex / self._cmapFile._gradients[self._gradientListModel._currentIndex].colorCount,
                    *map(
                        lambda cmapEntry: cmapEntry.y,
                        cmap,
                    ),
                ),
                OptimizationModel.Polynomial(
                    colorIndex / self._cmapFile._gradients[self._gradientListModel._currentIndex].colorCount,
                    *map(
                        lambda cmapEntry: cmapEntry.z,
                        cmap,
                    ),
                ),
            ))
        # colors = ColorSpace.SortByCIEH(colors)
        self._cmapFile._gradients[self._gradientListModel._currentIndex]._colors = colors
        index = self._gradientListModel._currentIndex
        self.updateFromCmapFile()
        self._gradientListModel.changeCurrent(index)

    def startApplication(
        self: Self,
    ) -> None:
        QApplication.exec()
