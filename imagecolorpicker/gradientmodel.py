from __future__ import annotations

import typing
from PyQt6.QtCore import *
from PyQt6.QtCore import QModelIndex, QObject, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from typing import *
from imagecolorpicker.colorgradient import GradientMix, GradientWeight, ColorGradient, DefaultGradient
from imagecolorpicker.color import Color
from glm import vec3

class GradientModel(QAbstractTableModel):
    ColumnTitles = [
        "Name",
        "wLin",
        "wRgb",
        "wOkLab",
    ]

    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._allColorMaps: List[Tuple[GradientWeight, GradientMix, List[vec3]]] = []
        self._gradient: ColorGradient = DefaultGradient
        self._linearWeights: List[float] = self._gradient.determineWeights(GradientWeight.Unweighted)
        self._rgbWeights: List[float] = self._gradient.determineWeights(GradientWeight.RGB)
        self._oklabWeights: List[float] = self._gradient.determineWeights(GradientWeight.Oklab)

    def columnCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(GradientModel.ColumnTitles)

    def rowCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(self._gradient._colors)
    
    def load(
        self: Self,
        allColorMaps: List[Tuple[GradientWeight, GradientMix, List[vec3]]],
        gradient: ColorGradient,
    ) -> None:
        self.beginResetModel()
        self._allColorMaps = allColorMaps
        self._gradient = gradient
        self._linearWeights: List[float] = self._gradient.determineWeights(GradientWeight.Unweighted)
        self._rgbWeights: List[float] = self._gradient.determineWeights(GradientWeight.RGB)
        self._oklabWeights: List[float] = self._gradient.determineWeights(GradientWeight.Oklab)
        self.endResetModel()
    
    def data(
        self: Self,
        index: QModelIndex,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return QVariant()
        
        color: vec3 = self._gradient._colors[index.row()]._color
        if role == Qt.ItemDataRole.DisplayRole:    
            if index.column() == 0:
                return QColor.fromRgbF(*color)
            elif index.column() == 1:
                return self._linearWeights[index.row()]
            elif index.column() == 2:
                return self._rgbWeights[index.row()]
            elif index.column() == 3:
                return self._oklabWeights[index.row()]
            
        elif role == Qt.ItemDataRole.BackgroundRole:
            return QColor.fromRgbF(*color)
        elif role == Qt.ItemDataRole.ForegroundRole:
            return QColor(Qt.GlobalColor.black if 0.299 * color.x + 0.587 * color.y + 0.114 * color.z > 186.0 / 255. else Qt.GlobalColor.white)

        return QVariant()

    def headerData(
        self: Self,
        section: int,
        orientation: Qt.Orientation,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()

        if orientation == Qt.Orientation.Horizontal:
            return GradientModel.ColumnTitles[section]
        else:
            return section

    def flags(
        self: Self,
        index: QModelIndex = QModelIndex(),
    ) -> Qt.ItemFlag:
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def setData(
        self: Self,
        index: QModelIndex,
        value: Any,
        role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        
        color: QColor = value
        newColors: List[vec3] = self._gradient._colors
        newColors[index.row()] = Color(color.redF(), color.greenF(), color.blueF())
        self._gradient = ColorGradient(*newColors)

        self._allColorMaps = self._gradient.allColorMaps()
        self._linearWeights: List[float] = self._gradient.determineWeights(GradientWeight.Unweighted)
        self._rgbWeights: List[float] = self._gradient.determineWeights(GradientWeight.RGB)
        self._oklabWeights: List[float] = self._gradient.determineWeights(GradientWeight.Oklab)

        return True
