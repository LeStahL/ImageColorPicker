from __future__ import annotations

from PyQt6.QtCore import *
from PyQt6.QtCore import QModelIndex, QObject, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from typing import *
from imagecolorpicker.colorgradient import GradientMix, GradientWeight, ColorGradient, DefaultGradient1
from glm import vec3
from .gradientcolorcolumntype import GradientColorColumnType


class GradientColorModel(QAbstractTableModel):
    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._gradient: Optional[ColorGradient] = None
        self._columnList: list[GradientColorColumnType] = [
            GradientColorColumnType.Name,
            GradientColorColumnType.Weight,
        ]

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
        columnType: GradientColorColumnType = self._columnList[index.column()]
        if roleEnum == Qt.ItemDataRole.DisplayRole:
            if columnType == GradientColorColumnType.Name:
                color = self._gradient._colors[index.row()]
                return QColor.fromRgbF(color.x, color.y, color.z).name()
            elif columnType == GradientColorColumnType.Weight:
                return self._gradient.weights[index.row()]
        elif roleEnum == Qt.ItemDataRole.BackgroundRole:
            color = self._gradient._colors[index.row()]
            return QColor.fromRgbF(color.x, color.y, color.z)
        elif roleEnum == Qt.ItemDataRole.ForegroundRole:
            color = self._gradient._colors[index.row()]
            return QColor(Qt.GlobalColor.black if 0.299 * color.x + 0.587 * color.y + 0.114 * color.z > 186.0 / 255. else Qt.GlobalColor.white)

    def columnCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(self._columnList)

    def rowCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        if self._gradient is None:
            return 0
        return len(self._gradient._colors)

    def headerData(
        self: Self,
        section: int,
        orientation: Qt.Orientation,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()

        if orientation == Qt.Orientation.Horizontal:
            return self._columnList[section].name
        else:
            return section

    def flags(
        self: Self,
        index: QModelIndex = QModelIndex(),
    ) -> Qt.ItemFlag:
        flags = super().flags(index)
        if not index.isValid() or self._gradient is None:
            return flags
        
        columnType: GradientColorColumnType = self._columnList[index.column()]
        if columnType == GradientColorColumnType.Name:
            flags = flags | Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(
        self: Self,
        index: QModelIndex,
        value: Any,
        role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid() or self._gradient is None:
            return False
        
        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        columnType: GradientColorColumnType = self._columnList[index.column()]
        if roleEnum == Qt.ItemDataRole.EditRole:
            if columnType == GradientColorColumnType.Name:
                color = QColor(value)
                self._gradient._colors[index.row()] = vec3(color.redF(), color.greenF(), color.blueF())
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                return True
        return False

    def updateColor(self: Self, row: int, color: QColor) -> None:
        self._gradient._colors[row] = vec3(color.redF(), color.greenF(), color.blueF())
        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount()), [Qt.ItemDataRole.EditRole])
        