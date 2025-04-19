from PyQt6.QtCore import (
    QObject,
    QModelIndex,
    QAbstractItemModel,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QWidget,
    QComboBox,
)
from PyQt6.QtGui import (
    QPainter,
)
from typing import (
    Self,
    Optional,
)
from ..model.gradientpropertycolumntype import GradientPropertyColumnType
from ..model.gradientpropertyrowtype import GradientPropertyRowType
from ..colorgradient import ColorGradient, FitModel
from ..widgets.gradientwidget.gradientwidget import GradientWidget
from ..colorspace import ColorSpaceType
from ..colorgradient import (
    Observer,
    FitAlgorithm,
    FitModel,
    Illuminant,
    Wraparound,
)
from enum import EnumMeta

class GradientPropertyDelegate(QStyledItemDelegate):
    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

    def enumComboBox(
        self: Self,
        parent: Optional[QWidget],
        index: QModelIndex,
        enumType: EnumMeta,
    ) -> QComboBox:
        comboBox: QComboBox = QComboBox(parent)
        comboBox.addItems([element.name for element in enumType])
        comboBox.setCurrentText(index.data())
        return comboBox

    def createEditor(
        self: Self,
        parent: Optional[QWidget],
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> Optional[QWidget]:
        columnType: GradientPropertyColumnType = index.model()._columnList[index.column()]
        rowType: GradientPropertyRowType = index.model()._rowList[index.row()]
        if columnType == GradientPropertyColumnType.Value:
            if rowType == GradientPropertyRowType.Model:
                return self.enumComboBox(parent, index, FitModel)
            elif rowType == GradientPropertyRowType.Wraparound:
                return self.enumComboBox(parent, index, Wraparound)
            elif rowType in [
                GradientPropertyRowType.WeightColorSpace,
                GradientPropertyRowType.MixColorSpace,
            ]:
                return self.enumComboBox(parent, index, ColorSpaceType)
            elif rowType == GradientPropertyRowType.Illuminant:
                return self.enumComboBox(parent, index, Illuminant)
            elif rowType == GradientPropertyRowType.Observer:
                return self.enumComboBox(parent, index, Observer)
            elif rowType == GradientPropertyRowType.FitAlgorithm:
                return self.enumComboBox(parent, index, FitAlgorithm)
        return super().createEditor(parent, option, index)
