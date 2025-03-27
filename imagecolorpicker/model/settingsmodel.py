from PyQt6.QtCore import (
    QAbstractTableModel,
    QObject,
    QModelIndex,
    Qt,
    pyqtSignal,
    QPointF,
    QPoint,
    QSettings,
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
from .settingscolumntype import SettingsColumnType
from .settingsrowtype import SettingsRowType
from ..colorspace import ColorSpaceType
from ..language import Language
from ..representation import Representation
from ..delegate.gradientpropertydelegate import GradientPropertyDelegate


class SettingsModel(QAbstractTableModel):
    gradientPropertiesChanged: pyqtSignal = pyqtSignal()

    def __init__(
        self: Self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._columnList: list[SettingsColumnType] = [
            SettingsColumnType.Key,
            SettingsColumnType.Value,
        ]
        self._rowList: list[SettingsRowType] = [
            SettingsRowType.CopyLanguage,
            SettingsRowType.CopyRepresentation,
        ]

    def data(
        self: Self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole.value,
    ) -> Any:
        if not index.isValid():
            return

        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        columnType: SettingsColumnType = self._columnList[index.column()]
        rowType: SettingsRowType = self._rowList[index.row()]
        if roleEnum == Qt.ItemDataRole.DisplayRole:
            if columnType == SettingsColumnType.Key:
                return rowType.name
            elif columnType == SettingsColumnType.Value:
                if rowType == SettingsRowType.CopyLanguage:
                    return QSettings().value(rowType.value, Language.GLSL.name)
                elif rowType == SettingsRowType.CopyRepresentation:
                    return QSettings().value(rowType.value, Representation.ColorMap.name)

    def setData(
        self: Self,
        index: QModelIndex,
        value: str,
        role: int = Qt.ItemDataRole.EditRole.value,
    ) -> bool:
        if not index.isValid():
            return False
        
        roleEnum: Qt.ItemDataRole = Qt.ItemDataRole(role)
        columnType: SettingsColumnType = self._columnList[index.column()]
        rowType: SettingsRowType = self._rowList[index.row()]
        if roleEnum == Qt.ItemDataRole.EditRole:
            if columnType == SettingsColumnType.Value:
                QSettings().setValue(rowType.value, value)
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
        columnType: SettingsColumnType = self._columnList[index.column()]
        if columnType == SettingsColumnType.Value:
            flags = flags | Qt.ItemFlag.ItemIsEditable
        return flags

    @property
    def language(self: Self) -> Language:
        return Language[self.data(self.index(
            self._rowList.index(SettingsRowType.CopyLanguage),
            self._columnList.index(SettingsColumnType.Value),
        ))]
    
    @property
    def representation(self: Self) -> Representation:
        return Representation[self.data(self.index(
            self._rowList.index(SettingsRowType.CopyRepresentation),
            self._columnList.index(SettingsColumnType.Value),
        ))]
