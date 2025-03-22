from PyQt6.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QBrush,
    QPen,
    QColor,
    QFont,
    QPalette,
)
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
)
from PyQt6.QtCore import (
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QTimer,
)
from typing import (
    Self,
    Optional,
)
from imagecolorpicker.colorgradient import (
    ColorGradient,
    GradientWeight,
    GradientMix,
    DefaultGradient1,
)
from sys import argv
from datetime import datetime, timedelta


class GradientWidget(QWidget):
    WeightDotSize: int = 4

    def __init__(
        self: Self,
        gradient: ColorGradient,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._gradient: ColorGradient = gradient

    def paintEvent(
        self: Self,
        a0: Optional[QPaintEvent],
    ) -> None:
        super().paintEvent(a0)

        self.paint(self.rect())

    def paint(
        self: Self,
        rect: QRect,
        painter: Optional[QPainter] = None,
    ) -> None:
        if painter is None:
            painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        brush: QBrush = QBrush(self._gradient.linearGradient(rect.x(), rect.width()))
        painter.setBrush(brush)
        painter.fillRect(QRectF(rect.x(), rect.y(), rect.width(), rect.height() - GradientWidget.WeightDotSize), brush)

        pen: QPen = QPen()
        pen.setWidth(2)
        pen.setBrush(brush)
        painter.setPen(pen)

        for weight in self._gradient.weights:
            painter.drawLine(QPointF(rect.x() + weight * rect.width(), rect.y() + rect.height() - 3 * GradientWidget.WeightDotSize), QPointF(rect.x() + weight * rect.width(), rect.y() + rect.height() - 2))

if __name__ == '__main__':
    app: QApplication = QApplication(argv)
    gradientWidget: GradientWidget = GradientWidget(DefaultGradient1)
    gradientWidget.show()
    app.exec()
