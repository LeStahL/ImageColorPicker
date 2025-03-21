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
    FontSize: int = 9
    CursorTimeout: float = 2.

    def __init__(
        self: Self,
        gradient: ColorGradient,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._gradient: ColorGradient = gradient
        self._lastMoveEvent: datetime = datetime.now() - timedelta(seconds=2 * GradientWidget.CursorTimeout)
        self._lastMovePosition: float = 0.

        self.setMouseTracking(True)

        self._timer: QTimer = QTimer()

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

        palette: QPalette = QApplication.palette()

        painter.fillRect(rect, brush)
        backgroundColor: QColor = QColor(palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.Window))
        painter.setBrush(backgroundColor)
        painter.fillRect(QRectF(rect.x(), rect.y() + rect.height() - 1 * GradientWidget.WeightDotSize - 1., rect.width(), 3 * GradientWidget.WeightDotSize + 1.), backgroundColor)
        painter.setBrush(brush)

        pen: QPen = QPen()
        foregroudColor: QColor = QColor(palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.WindowText))
        pen.setColor(foregroudColor)
        pen.setWidth(4)
        painter.setPen(pen)

        font: QFont = QFont()
        font.setPointSizeF(GradientWidget.FontSize)
        font.setWeight(QFont.Weight.ExtraBold)
        painter.setFont(font)

        for weight in self._gradient.weights:
            pen.setBrush(brush)
            painter.setPen(pen)
            painter.drawLine(QPointF(rect.x() + weight * rect.width(), rect.y() + rect.height() - 3 * GradientWidget.WeightDotSize), QPointF(rect.x() + weight * rect.width(), rect.y() + rect.height() - 2))

        pen.setWidth(2)
        # Draw cursor
        if (datetime.now() - self._lastMoveEvent).total_seconds() < GradientWidget.CursorTimeout:
            painter.setBrush(backgroundColor)
            painter.fillRect(QRectF(rect.x() + self._lastMovePosition * rect.width(), rect.y() + rect.height() - 3 * GradientWidget.WeightDotSize - 1., 40., 3 * GradientWidget.WeightDotSize + 1.), backgroundColor)
        
            pen.setColor(foregroudColor)
            painter.setPen(pen)
            painter.drawText(
                QPointF(rect.x() + self._lastMovePosition * rect.width() + 2 * GradientWidget.WeightDotSize, rect.y() + rect.height() - 1),
                f'{self._lastMovePosition:.2f}',
            )
            painter.drawLine(QPointF(rect.x() + self._lastMovePosition * rect.width(), rect.y()), QPointF(rect.x() + self._lastMovePosition * rect.width(), rect.y() + rect.height()))
            pen.setColor(backgroundColor)
            painter.setPen(pen)
            painter.drawLine(QPointF(rect.x() + self._lastMovePosition * rect.width() + 1, rect.y()), QPointF(rect.x() + self._lastMovePosition * rect.width() + 1, rect.y() + rect.height()))

    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        super().mouseMoveEvent(a0)
        self._lastMoveEvent = datetime.now()
        self._lastMovePosition = (a0.pos().x() - self.rect().x()) / self.width()
        self.update()
        self._timer.singleShot(int(1000 * GradientWidget.CursorTimeout) + 1000, self.update)
        

if __name__ == '__main__':
    app: QApplication = QApplication(argv)
    gradientWidget: GradientWidget = GradientWidget(DefaultGradient1)
    gradientWidget.show()
    app.exec()
