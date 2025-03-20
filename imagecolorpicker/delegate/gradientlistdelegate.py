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
from ..model.gradientlistcolumntype import (
    GradientListColumnType,
)
from ..colorgradient import ColorGradient, FitModel
from ..widgets.gradientwidget.gradientwidget import GradientWidget


class GradientListDelegate(QStyledItemDelegate):
    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        
    def paint(
        self: Self,
        painter: Optional[QPainter],
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        if index.model()._columnList[index.column()] == GradientListColumnType.Preview:
            self._gradientPreview: GradientWidget = GradientWidget(index.data())
            self._gradientPreview.paint(option.rect, painter)
            return
        return super().paint(painter, option, index)

    def createEditor(
        self: Self,
        parent: Optional[QWidget],
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> Optional[QWidget]:
        if index.model()._columnList[index.column()] == GradientListColumnType.Model:
            comboBox: QComboBox = QComboBox(parent)
            comboBox.addItems([fitModel.name for fitModel in FitModel])
            comboBox.setCurrentText(index.data())
            return comboBox
        return super().createEditor(parent, option, index)
