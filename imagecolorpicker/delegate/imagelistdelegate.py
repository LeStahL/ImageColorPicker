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
    QImage,
)
from typing import (
    Self,
    Optional,
)

class ImageListDelegate(QStyledItemDelegate):
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
        image: QImage = index.data()
        painter.drawImage(option.rect, image, image.rect())
