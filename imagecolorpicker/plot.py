from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
)
from imagecolorpicker.colorgradient import ColorGradient
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from typing import (
    Self,
)
import matplotlib
import matplotlib.pyplot
try:
    matplotlib.use('QtAgg')
except ImportError:
    print("Headless means no Qt integration.")
from pathlib import Path
from numpy import linspace
from imagecolorpicker.colorgradient import DefaultGradient1
from sys import argv


class Plot(QWidget):
    def __init__(
        self: Self,
    ) -> None:
        super().__init__()
        self._fig, (self._ax_data, self._ax_res) = matplotlib.pyplot.subplots(
            2, 1, sharex=True,
            gridspec_kw={"height_ratios": [3, 1]},
            figsize=(8, 6)
        )
        self.canvas = FigureCanvasQTAgg(self._fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self._t = linspace(0., 1., 250)

    def loadGradient(
        self: Self,
        gradient: ColorGradient,
    ) -> None:
        self._ax_data.clear()
        self._ax_res.clear()

        colors = list(map(gradient.evaluate, self._t))
        fitted_colors = list(map(gradient.evaluateFit, self._t))

        residuals = list(map(lambda colorIndex: colors[colorIndex] - fitted_colors[colorIndex], range(len(colors))))
        squaresum = sum(map(lambda residual: residual * residual, residuals))

        self._ax_data.scatter(self._t, list(map(lambda color: color.x, colors)), label="Red", color="tab:red", s=2)
        self._ax_data.plot(self._t, list(map(lambda color: color.x, fitted_colors)), label="Red fit", color="tab:red")
        self._ax_data.scatter(self._t, list(map(lambda color: color.y, colors)), label="Green", color="tab:green", s=2)
        self._ax_data.plot(self._t, list(map(lambda color: color.y, fitted_colors)), label="Green fit", color="tab:green")
        self._ax_data.scatter(self._t, list(map(lambda color: color.z, colors)), label="Blue", color="tab:blue", s=2)
        self._ax_data.plot(self._t, list(map(lambda color: color.z, fitted_colors)), label="Blue fit", color="tab:blue")
        # self._ax_data.legend()
        self._ax_data.set_ylabel("RGB Comp.")
        self._ax_data.set_title(f"Approx. CMAP {gradient._weightColorSpace.name} weight {DefaultGradient1._mixColorSpace.name} mix @ {squaresum.x:.2f} / {squaresum.y:.2f} / {squaresum.z:.2f}")
        self._ax_data.grid()

        self._ax_res.axhline(0, color="black", linewidth=1)
        self._ax_res.scatter(self._t, list(map(lambda color: color.x, residuals)), color="tab:red", s=2)
        self._ax_res.scatter(self._t, list(map(lambda color: color.y, residuals)), color="tab:green", s=2)
        self._ax_res.scatter(self._t, list(map(lambda color: color.z, residuals)), color="tab:blue", s=2)
        self._ax_res.set_ylabel("Residuals")
        self._ax_res.set_xlabel("t")
        self._ax_res.grid()
        
        self._fig.tight_layout()
        self.canvas.draw()

    def save(self: Self, file: Path) -> None:
        self._fig.savefig(file)

if __name__ == '__main__':
    app = QApplication(argv)
    plot = Plot()
    plot.loadGradient(DefaultGradient1)
    plot.show()
    app.exec()
