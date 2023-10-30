from __future__ import annotations

from PyQt6.QtCore import *
from PyQt6.QtCore import QModelIndex, QObject, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from typing import *
from enum import IntEnum, StrEnum
from parse import parse

class Language(IntEnum):
    GLSL = 0x0
    HLSL = 0x1
    Python = 0x2
    C = 0x4
    CSS = 0x5

class Representation(StrEnum):
    Vec3 = 'vec3({redf:.2f}, {greenf:.2f}, {bluef:.2f})'
    Vec4 = 'vec4({redf:.2f}, {greenf:.2f}, {bluef:.2f}, 1.)'
    Float3 = '{{{redf:.2f}f, {greenf:.2f}f, {bluef:.2f}f}}'
    Float4 = '{{{redf:.2f}f, {greenf:.2f}f, {bluef:.2f}f, 1.0f}}'
    ListInt = '[{red}, {green}, {blue}]'
    ListFloat = '[{redf:.2f}, {greenf:.2f}, {bluef:.2f}]'
    QColor = 'QColor({red}, {green}, {blue})'
    color_t = '{{{redf:.2f}, {greenf:.2f}, {bluef:.2f}}}'
    Hex = '{name}'
    NearLinRgb = 'cmap_UnweightedRGB{slug}({nearLinRGB:.2f})'
    NearLinOklab = 'cmap_UnweightedOklab{slug}({nearLinOklab:.2f})'
    NearRgbRgb = 'cmap_RGBRGB{slug}({nearRGBRGB:.2f})'
    NearRgbOklab = 'cmap_RGBOklab{slug}({nearRGBOklab:.2f})'
    NearOklabRgb = 'cmap_OklabRGB{slug}({nearOklabRGB:.2f})'
    NearOklabOklab = 'cmap_OklabOklab{slug}({nearOklabOklab:.2f})'

class CodeModel(QAbstractTableModel):
    ColumnTitles = [
        "Language",
        "Repr.",
        "Value",
    ]
    RowMetadata = [
        (Language.GLSL, Representation.Vec3, 'vec3'),
        (Language.GLSL, Representation.Vec4, 'vec4'),
        (Language.HLSL, Representation.Float3, 'float3'),
        (Language.HLSL, Representation.Float4, 'float4'),
        (Language.Python, Representation.ListInt, 'List[int]'),
        (Language.Python, Representation.ListFloat, 'List[float]'),
        (Language.Python, Representation.QColor, 'QColor'),
        (Language.C, Representation.color_t, 'color_t'),
        (Language.CSS, Representation.Hex, 'hex'),
        (Language.GLSL, Representation.NearLinOklab, 'Near Lin/Oklab'),
        (Language.GLSL, Representation.NearLinRgb, 'Near Lin/RGB'),
        (Language.GLSL, Representation.NearRgbOklab, 'Near RGB/Oklab'),
        (Language.GLSL, Representation.NearRgbRgb, 'Near RGB/RGB'),
        (Language.GLSL, Representation.NearOklabOklab, 'Near Oklab/Oklab'),
        (Language.GLSL, Representation.NearOklabRgb, 'Near Oklab/RGB'),
    ]

    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._color = QColor.fromRgb(0,0,0)
        self._slug = "_example"
        self._nearestWeights = [0.] * 6

    def columnCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(CodeModel.ColumnTitles)

    def rowCount(
        self: Self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:
        return len(CodeModel.RowMetadata)
    
    def load(
        self: Self,
        color: QColor,
        nearestWeights: List[float],
        slug: str,
    ):
        self.beginResetModel()
        self._color = color
        self._nearestWeights = nearestWeights
        self._slug = slug
        self.endResetModel()

    def data(
        self: Self,
        index: QModelIndex,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return QVariant()
        
        if role == Qt.ItemDataRole.DisplayRole:
            language, representation, prettyName = CodeModel.RowMetadata[index.row()]
            
            if index.column() == 0:
                return language.name
            elif index.column() == 1:
                return prettyName
            elif index.column() == 2:
                return representation.value.format(
                    redf=self._color.redF(),
                    greenf=self._color.greenF(),
                    bluef=self._color.blueF(),
                    red=self._color.red(),
                    green=self._color.green(),
                    blue=self._color.blue(),
                    name=self._color.name(),
                    slug=self._slug,
                    nearLinRGB=self._nearestWeights[0],
                    nearLinOklab=self._nearestWeights[1],
                    nearRGBRGB=self._nearestWeights[2],
                    nearRGBOklab=self._nearestWeights[3],
                    nearOklabRGB=self._nearestWeights[4],
                    nearOklabOklab=self._nearestWeights[5],
                )
            
        elif role == Qt.ItemDataRole.BackgroundRole:
            return QColor(225, 225, 225) if index.row() % 2 == 0 else QColor(183, 183, 183)
        elif role == Qt.ItemDataRole.ForegroundRole:
            return QColor(Qt.GlobalColor.black)

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
            return CodeModel.ColumnTitles[section]
        else:
            return section
        
    def flags(
        self: Self,
        index: QModelIndex = QModelIndex(),
    ) -> Qt.ItemFlag:
        if index.column() == 2:
            return super().flags(index) | Qt.ItemFlag.ItemIsEditable
        return super().flags(index)

    def setData(
        self: Self,
        index: QModelIndex,
        value: Any,
        role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        
        _, representation, _ = CodeModel.RowMetadata[index.row()]
        
        result = parse(representation.value, value)
        if result is None:
            return False

        if 'redf' in result and 'greenf' in result and 'bluef' in result:
            self._color = QColor.fromRgbF(result['redf'], result['greenf'], result['bluef'])
        elif 'red' in result and 'green' in result and 'blue' in result:
            self._color = QColor.fromRgb(result['red'], result['green'], result['blue'])
        elif 'name' in result:
            self._color = QColor(result['name'])
        else:
            return False
        
        self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), self.columnCount()), [role])

        return True
