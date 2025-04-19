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
from .gradientpropertycolumntype import GradientPropertyColumnType
from .gradientpropertyrowtype import GradientPropertyRowType
from ..colorspace import ColorSpaceType
from ..colorgradient import (
    Observer,
    FitAlgorithm,
    FitModel,
    Illuminant,
    Wraparound,
)
from ..delegate.gradientpropertydelegate import GradientPropertyDelegate


class GradientPropertyModel(QAbstractTableModel):
    gradientPropertiesChanged: pyqtSignal = pyqtSignal()

    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._columnList: list[GradientPropertyColumnType] = [
            GradientPropertyColumnType.Key,
            GradientPropertyColumnType.Value,
        ]
        self._rowList: list[GradientPropertyRowType] = [
            GradientPropertyRowType.Name,
            GradientPropertyRowType.Degree,
            GradientPropertyRowType.Model,
            GradientPropertyRowType.Wraparound,
            GradientPropertyRowType.MixColorSpace,
            GradientPropertyRowType.WeightColorSpace,
            GradientPropertyRowType.Illuminant,
            GradientPropertyRowType.Observer,
            GradientPropertyRowType.FitAlgorithm,
            GradientPropertyRowType.FitAmount,
            GradientPropertyRowType.MaxFitIterationCount,
        ]

        self._gradient: Optional[ColorGradient] = None

    def loadGradient(
        self: Self,
        gradient: Optional[ColorGradient],
    ) -> None:
        self.beginResetModel()
        self._gradient = gradient
        self.endResetModel()

    def data(
        self: Self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole.value,
    ) -> Any:
        if not index.isValid() or self._gradient is None:
            return

        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        columnType: GradientPropertyColumnType = self._columnList[index.column()]
        rowType: GradientPropertyRowType = self._rowList[index.row()]
        if roleEnum == Qt.ItemDataRole.DisplayRole:
            if columnType == GradientPropertyColumnType.Key:
                return rowType.name
            elif columnType == GradientPropertyColumnType.Value:
                if rowType == GradientPropertyRowType.Name:
                    return self._gradient._name
                elif rowType == GradientPropertyRowType.Degree:
                    return self._gradient._degree
                elif rowType == GradientPropertyRowType.WeightColorSpace:
                    return self._gradient._weightColorSpace.name
                elif rowType == GradientPropertyRowType.MixColorSpace:
                    return self._gradient._mixColorSpace.name
                elif rowType == GradientPropertyRowType.Observer:
                    return self._gradient._observer.name
                elif rowType == GradientPropertyRowType.Illuminant:
                    return self._gradient._illuminant.name
                elif rowType == GradientPropertyRowType.Model:
                    return self._gradient._model.name
                elif rowType == GradientPropertyRowType.Wraparound:
                    return self._gradient._wraparound.name
                elif rowType == GradientPropertyRowType.FitAlgorithm:
                    return self._gradient._fitAlgorithm.name
                elif rowType == GradientPropertyRowType.MaxFitIterationCount:
                    return self._gradient._maxFitIterationCount
                elif rowType == GradientPropertyRowType.FitAmount:
                    return self._gradient._fitAmount

    def setData(
        self: Self,
        index: QModelIndex,
        value: str,
        role: int = Qt.ItemDataRole.EditRole.value,
    ) -> bool:
        if not index.isValid() or self._gradient is None:
            return False
        
        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        columnType: GradientPropertyColumnType = self._columnList[index.column()]
        rowType: GradientPropertyRowType = self._rowList[index.row()]
        if roleEnum == Qt.ItemDataRole.EditRole:
            if columnType == GradientPropertyColumnType.Value:
                if rowType == GradientPropertyRowType.Name:
                    self._gradient._name = value
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.Degree:
                    self._gradient._degree = int(value)
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.WeightColorSpace:
                    self._gradient._weightColorSpace = ColorSpaceType[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.MixColorSpace:
                    self._gradient._mixColorSpace = ColorSpaceType[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.Observer:
                    self._gradient._observer = Observer[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.Illuminant:
                    self._gradient._illuminant = Illuminant[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.Model:
                    self._gradient._model = FitModel[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.Wraparound:
                    self._gradient._wraparound = Wraparound[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.FitAlgorithm:
                    self._gradient._fitAlgorithm = FitAlgorithm[value]
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.MaxFitIterationCount:
                    self._gradient._maxFitIterationCount = int(value)
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
                elif rowType == GradientPropertyRowType.FitAmount:
                    self._gradient._fitAmount = int(value)
                    self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                    return True
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
        return len(self._rowList)
    
    def flags(self: Self, index: QModelIndex) -> Qt.ItemFlag:
        flags: Qt.ItemFlag = super().flags(index)
        columnType: GradientPropertyColumnType = self._columnList[index.column()]
        if columnType == GradientPropertyColumnType.Value:
            flags = flags | Qt.ItemFlag.ItemIsEditable
        return flags

if __name__ == '__main__':
    app = QApplication(argv)

    tableView: QTableView = QTableView()

    delegate: GradientPropertyDelegate = GradientPropertyDelegate()
    tableView.setItemDelegate(delegate)

    model: GradientPropertyModel = GradientPropertyModel()
    tableView.setModel(model)

    model.loadGradient(DefaultGradient1)

    tableView.show()

    app.exec()
