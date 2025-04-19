from PyQt6.QtCore import (
    QAbstractTableModel,
    QObject,
    QModelIndex,
    Qt,
    pyqtSignal,
    QPointF,
    QPoint,
)
from PyQt6.QtGui import (
    QPalette,
    QFont,
    QPen,
    QColor,
)
from PyQt6.QtWidgets import (
    QApplication,
    QTableView,
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
from sys import argv
from ..delegate.gradientlistdelegate import GradientListDelegate
from .gradientlistcolumntype import GradientListColumnType
from copy import deepcopy
from ..colorspace import ColorSpaceType


class GradientListModel(QAbstractTableModel):
    currentGradientChanged: pyqtSignal = pyqtSignal(ColorGradient)

    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._columnList: list[GradientListColumnType] = [
            GradientListColumnType.Name,
            GradientListColumnType.Preview,
            GradientListColumnType.Model,
            GradientListColumnType.Degree,
        ]

        self._gradientList: list[ColorGradient] = []
        self._currentIndex: int = 0

    def loadGradientList(
        self: Self,
        gradientList: Optional[list[ColorGradient]],
    ) -> None:
        self.beginResetModel()
        self._gradientList = gradientList or []
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
        columnType: GradientListColumnType = self._columnList[index.column()]
        if roleEnum == Qt.ItemDataRole.DisplayRole:
            if columnType == GradientListColumnType.Name:
                return self._gradientList[index.row()]._name
            elif columnType == GradientListColumnType.Degree:
                return self._gradientList[index.row()]._degree
            elif columnType == GradientListColumnType.Model:
                return self._gradientList[index.row()]._model.name
            elif columnType == GradientListColumnType.Preview:
                return self._gradientList[index.row()]
        
        if roleEnum == Qt.ItemDataRole.FontRole:
            if index.row() == self._currentIndex:
                font: QFont = QFont()
                font.setBold(True)
                return font

    def setData(
        self: Self,
        index: QModelIndex,
        value: str,
        role: int = Qt.ItemDataRole.EditRole.value,
    ) -> bool:
        if not index.isValid():
            return False
        
        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        columnType: GradientListColumnType = self._columnList[index.column()]
        if roleEnum == Qt.ItemDataRole.EditRole:
            if columnType == GradientListColumnType.Name:
                self._gradientList[index.row()]._name = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])        
            elif columnType == GradientListColumnType.Degree:
                try:
                    self._gradientList[index.row()]._degree = int(value)
                    self._gradientList[index.row()]._update()
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                except:
                    return False
            elif columnType == GradientListColumnType.Model:
                try:
                    self._gradientList[index.row()]._model = FitModel[value]
                    self._gradientList[index.row()]._update()
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
            return self._columnList[section].name

        if orientation == Qt.Orientation.Vertical:
            return section

    def columnCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(self._columnList)

    def rowCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(self._gradientList)

    def flags(self: Self, index: QModelIndex) -> Qt.ItemFlag:
        flags: Qt.ItemFlag = super().flags(index)
        columnType: GradientListColumnType = self._columnList[index.column()]
        if columnType in [
            GradientListColumnType.Name,
            GradientListColumnType.Degree,
            GradientListColumnType.Model,
        ]:
            flags = flags | Qt.ItemFlag.ItemIsEditable
        return flags
    
    def changeCurrent(
        self: Self,
        newIndex: int,
    ) -> None:
        oldIndex: int = self._currentIndex
        self._currentIndex = newIndex
        self.dataChanged.emit(self.index(oldIndex, 0), self.index(oldIndex, self.columnCount()), [Qt.ItemDataRole.EditRole])
        self.dataChanged.emit(self.index(newIndex, 0), self.index(newIndex, self.columnCount()), [Qt.ItemDataRole.EditRole])
        self.currentGradientChanged.emit(self._gradientList[self._currentIndex])

    def updateCurrentGradient(self: Self) -> None:
        self._gradientList[self._currentIndex]._update()
        self.dataChanged.emit(
            self.index(self._currentIndex, 0),
            self.index(self._currentIndex, self.columnCount()),
            [Qt.ItemDataRole.DisplayRole],
        )

    def copyCurrentGradientWithColorSpaces(self: Self, weightColorSpace: ColorSpaceType, mixColorSpace: ColorSpaceType) -> ColorGradient:
        result: ColorGradient = deepcopy(self._gradientList[self._currentIndex])
        result._weightColorSpace = weightColorSpace
        result._mixColorSpace = mixColorSpace
        result._name = f'{weightColorSpace.name}:{mixColorSpace.name}'
        result._update()
        return result

if __name__ == '__main__':
    app = QApplication(argv)

    tableView: QTableView = QTableView()

    delegate: GradientListDelegate = GradientListDelegate()
    tableView.setItemDelegate(delegate)
    tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    model: GradientListModel = GradientListModel()
    tableView.setModel(model)

    def rightClicked(position: QPoint) -> None:
        index: QModelIndex = tableView.indexAt(position)
        if index.isValid():
            model.changeCurrent(index.row())
    tableView.customContextMenuRequested.connect(rightClicked)
    
    gradientList: list[ColorGradient] = [
        DefaultGradient1,
        DefaultGradient2,
    ]
    model.loadGradientList(gradientList)

    tableView.show()

    app.exec()
