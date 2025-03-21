from typing import (
    Self,
    Optional,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
)
from PyQt6.QtGui import (
    QIcon,
    QColor,
    QImage,
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

        self.updateFromCmapFile()

    def updateFromCmapFile(
        self: Self,
    ) -> None:
        self._gradientListModel.loadGradientList(self._cmapFile._gradients)
        self._imageListModel.loadImageList(self._cmapFile._images)

    def _gradientListContextMenuRequested(self: Self, position: QPoint) -> None:
        index: QModelIndex = self._mainWindow._ui.gradientTableView.indexAt(position)
        if index.isValid():
            self._gradientListModel.changeCurrent(index.row())

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

    def startApplication(
        self: Self,
    ) -> None:
        QApplication.exec()
