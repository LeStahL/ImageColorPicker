from PyQt6.QtGui import (
    QPaintEvent,
    QPainter,
    QBrush,
    QPen,
    QColor,
)
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
)
from PyQt6.QtCore import (
    QPoint,
    QPointF,
)
from typing import (
    Self,
    Optional,
)
from imagecolorpicker.colorgradient import (
    ColorGradient,
    GradientWeight,
    GradientMix,
)
from imagecolorpicker.color import (
    Color,
)
from sys import argv


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

        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        brush: QBrush = QBrush(self._gradient.linearGradient(self.width()))

        painter.fillRect(self.rect(), brush)
        painter.setBrush(QColor('#000000'))

        pen: QPen = QPen()
        pen.setColor(QColor('#FFFFFF'))
        pen.setWidth(2)
        painter.setPen(pen)

        for weight in self._gradient.weights:
            painter.drawEllipse(
                QPointF(weight * self.width(), GradientWidget.WeightDotSize),
                GradientWidget.WeightDotSize,
                GradientWidget.WeightDotSize,
            )
            painter.drawEllipse(
                QPointF(weight * self.width(), self.height() - GradientWidget.WeightDotSize),
                GradientWidget.WeightDotSize,
                GradientWidget.WeightDotSize,
            )
            painter.drawText(
                QPointF(weight * self.width() + 2 * GradientWidget.WeightDotSize, self.height()),
                f'{weight:.2f}',
            )
        

if __name__ == '__main__':
    app: QApplication = QApplication(argv)
    gradientWidget: GradientWidget = GradientWidget(ColorGradient(
        "default gradient",
        7,
        GradientWeight.Oklab,
        GradientMix.Oklab,
        Color(0.15, 0.18, 0.26),
        Color(0.51, 0.56, 0.66),
        Color(0.78, 0.67, 0.68),
        Color(0.96, 0.75, 0.60),
        Color(0.97, 0.81, 0.55),
        Color(0.97, 0.61, 0.42),
        Color(0.91, 0.42, 0.34),
        Color(0.58, 0.23, 0.22),
    ))
    gradientWidget.show()
    app.exec()
