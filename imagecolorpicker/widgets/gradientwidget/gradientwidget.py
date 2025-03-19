from PyQt6.QtGui import (
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
)
from typing import (
    Self,
    Optional,
)
from imagecolorpicker.colorgradient import (
    ColorGradient,
    GradientWeight,
    GradientMix,
    DefaultGradient,
)
from imagecolorpicker.color import (
    Color,
)
from sys import argv


class GradientWidget(QWidget):
    WeightDotSize: int = 4
    FontSize: int = 9

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

        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        brush: QBrush = QBrush(self._gradient.linearGradient(self.width()))

        palette: QPalette = QApplication.palette()

        painter.fillRect(self.rect(), brush)
        backgroundColor: QColor = QColor(palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.Window))
        painter.setBrush(backgroundColor)
        painter.fillRect(QRectF(0., self.height() - 3 * GradientWidget.WeightDotSize - 1., self.width(), 3 * GradientWidget.WeightDotSize + 1.), backgroundColor)
        painter.setBrush(brush)

        pen: QPen = QPen()
        pen.setColor(QColor(palette.color(QPalette.ColorGroup.Normal, QPalette.ColorRole.WindowText)))
        # pen.setWidth(2)
        painter.setPen(pen)

        font: QFont = QFont()
        font.setPointSizeF(GradientWidget.FontSize)
        painter.setFont(font)

        for weight in self._gradient.weights:
            # painter.drawEllipse(
            #     QPointF(weight * self.width(), GradientWidget.WeightDotSize),
            #     GradientWidget.WeightDotSize,
            #     GradientWidget.WeightDotSize,
            # )
            painter.drawEllipse(
                QPointF(weight * self.width(), self.height() - GradientWidget.WeightDotSize - 1),
                GradientWidget.WeightDotSize,
                GradientWidget.WeightDotSize,
            )
            painter.drawText(
                QPointF(weight * self.width() + 2 * GradientWidget.WeightDotSize, self.height() - 1),
                f'{weight:.2f}',
            )
        

if __name__ == '__main__':
    app: QApplication = QApplication(argv)
    gradientWidget: GradientWidget = GradientWidget(DefaultGradient)
    gradientWidget.show()
    app.exec()
