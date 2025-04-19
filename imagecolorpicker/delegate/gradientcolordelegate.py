from PyQt6.QtCore import (
    QObject,
    QModelIndex,
    QAbstractItemModel,
    pyqtSignal,
    Qt,
)
from PyQt6.QtWidgets import (
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QWidget,
    QComboBox,
    QColorDialog,
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
)
from typing import (
    Self,
    Optional,
)
from ..model.gradientcolorcolumntype import GradientColorColumnType


class GradientColorDelegate(QStyledItemDelegate):
    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

    def createEditor(
        self: Self,
        parent: Optional[QWidget],
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> Optional[QWidget]:
        columnType: GradientColorColumnType = index.model()._columnList[index.column()]
        if columnType == GradientColorColumnType.Name:
            return QColorDialog()
        return super().createEditor(parent, option, index)

    def setEditorData(
        self: Self,
        editor: QWidget,
        index: QModelIndex,
    ) -> None:
        columnType: GradientColorColumnType = index.model()._columnList[index.column()]
        if columnType == GradientColorColumnType.Name:
            editor.setCurrentColor(QColor(index.data()))
        else:
            super().setEditorData(editor, index)

    def setModelData(
        self: Self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex,
    ) -> None:
        columnType: GradientColorColumnType = model._columnList[index.column()]
        if columnType == GradientColorColumnType.Name:
            model.setData(index, editor.currentColor().name(), Qt.ItemDataRole.EditRole)
        else:
            super().setModelData(editor, model, index)()
