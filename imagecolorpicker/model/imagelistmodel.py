from PyQt6.QtCore import (
    QAbstractTableModel,
    QAbstractListModel,
    QObject,
    QModelIndex,
    Qt,
    pyqtSignal,
    QPointF,
    QPoint,
    QSize,
)
from PyQt6.QtGui import (
    QPalette,
    QFont,
    QPen,
    QColor,
    QImage,
)
from PyQt6.QtWidgets import (
    QApplication,
    QTableView,
    QListView,
)
from typing import (
    Any,
    Self,
    Optional,
    Union,
)
from traceback import format_exc
from traceback import print_exc
from ..colorgradient import (
    ColorGradient,
    FitModel,
    DefaultGradient1,
    DefaultGradient2,
)
from importlib.resources import files
from pathlib import Path
from imagecolorpicker.widgets import pickablecolorlabel
from sys import argv
from ..delegate.gradientlistdelegate import GradientListDelegate
from .gradientlistcolumntype import GradientListColumnType
from ..delegate.imagelistdelegate import ImageListDelegate


class ImageListModel(QAbstractListModel):
    currentImageChanged: pyqtSignal = pyqtSignal(QImage)
    
    DefaultImageWidth: int = 256

    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._imageList: list[QImage] = []
        self._currentIndex: int = 0

    def loadImageList(
        self: Self,
        imageList: Optional[list[QImage]],
    ) -> None:
        self.beginResetModel()
        self._imageList = imageList or []
        self._currentIndex = 0
        self.endResetModel()

    def data(
        self: Self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole.value,
    ) -> Any:
        if not index.isValid():
            return

        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        if roleEnum == Qt.ItemDataRole.DisplayRole:
            return self._imageList[index.row()]
        
        elif roleEnum == Qt.ItemDataRole.SizeHintRole:
            image: QImage = self._imageList[index.row()]
            aspect = float(image.width()) / float(image.height())
            return QSize(ImageListModel.DefaultImageWidth, int(ImageListModel.DefaultImageWidth / aspect))

    
    def setData(
        self: Self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole.value,
    ) -> bool:
        if not index.isValid():
            return False
        
        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        if roleEnum == Qt.ItemDataRole.EditRole:
            try:
                self._imageList[index.row()] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                return True
            except:
                return False
        
        return False
    
    def headerData(
        self: Self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole.value,
    ) -> Any:
        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)

        if roleEnum != Qt.ItemDataRole.DisplayRole:
            return

        if orientation == Qt.Orientation.Horizontal:
            return "Preview"

        if orientation == Qt.Orientation.Vertical:
            return section

    def columnCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return 1

    def rowCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(self._imageList)
    
    def flags(self: Self, index: QModelIndex) -> Qt.ItemFlag:
        flags: Qt.ItemFlag = super().flags(index)
        return flags

    def changeCurrent(
        self: Self,
        newIndex: int,
    ) -> None:
        oldIndex: int = self._currentIndex
        self._currentIndex = newIndex
        self.dataChanged.emit(self.index(oldIndex, 0), self.index(oldIndex, self.columnCount()), [Qt.ItemDataRole.EditRole])
        self.dataChanged.emit(self.index(newIndex, 0), self.index(newIndex, self.columnCount()), [Qt.ItemDataRole.EditRole])
        self.currentImageChanged.emit(self._imageList[self._currentIndex])

if __name__ == '__main__':
    app = QApplication(argv)

    listView: QListView = QListView()

    imageListDelegate: ImageListDelegate = ImageListDelegate()
    listView.setItemDelegate(imageListDelegate)

    model: ImageListModel = ImageListModel()
    listView.setModel(model)

    image: QImage = QImage(str(files(pickablecolorlabel) / 'default.png'))
    imageList: list[QImage] = [
        image,
    ]

    model.loadImageList(imageList)
    
    listView.show()

    app.exec()
