from PyQt6.QtCore import (
    QObject,
    QModelIndex,
)
from PyQt6.QtWidgets import (
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QWidget,
    QComboBox,
)
from typing import (
    Self,
    Optional,
)
from ..model.settingscolumntype import SettingsColumnType
from ..model.settingsrowtype import SettingsRowType
from enum import EnumMeta
from ..language import Language
from ..representation import Representation

class SettingsDelegate(QStyledItemDelegate):
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
        columnType: SettingsColumnType = index.model()._columnList[index.column()]
        rowType: SettingsRowType = index.model()._rowList[index.row()]
        if columnType == SettingsColumnType.Value:
            if rowType == SettingsRowType.CopyLanguage:
                return self.enumComboBox(parent, index, Language)
            elif rowType == SettingsRowType.CopyRepresentation:
                return self.enumComboBox(parent, index, Representation)
        return super().createEditor(parent, option, index)
