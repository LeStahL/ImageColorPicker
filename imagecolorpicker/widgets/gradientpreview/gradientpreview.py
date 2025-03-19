from typing import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import *
from OpenGL.GL import *
from sys import argv
from os.path import dirname
from imagecolorpicker.colorspace import ColorSpaceType, ColorSpace, Observer, Illuminant
from imagecolorpicker.color import Color
from imagecolorpicker.colorgradient import DefaultGradient, GradientWeight, GradientMix, ColorGradient, FitModel
from imagecolorpicker.widgets.gradientwidget.gradientwidget import GradientWidget
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sys import argv
from glm import vec3

class GradientPreview(QOpenGLWidget):
    ShaderFile = "gradientpreview.frag"

    def __init__(
        self: Self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Widget,
    ) -> None:
        super().__init__(parent, flags)

        self._reload = False
        self.changeColorMaps(DefaultGradient.allColorMaps())

        self._resolutionLocation = None

        self._environment = Environment(
            loader=FileSystemLoader(dirname(__file__)),
            autoescape=select_autoescape(),
        )
        self._template = self._environment.get_template(GradientPreview.ShaderFile)

    def changeColorMaps(self: Self, colorMaps: List[Tuple[GradientWeight, GradientMix, List[vec3]]]) -> None:
        self._colorMaps = colorMaps
        self._reload = True
        self.update()

    def resizeGL(self: Self, width: int, height: int) -> None:
        super().resizeGL(width, height)
        self.update()

    def paintGL(self: Self) -> None:
        super().paintGL()

        if self._reload:
            glUseProgram(0)

            shader = glCreateShader(GL_FRAGMENT_SHADER)
            self._source = self._template.render(colorMaps=self._colorMaps)
            glShaderSource(shader, self._source)
            glCompileShader(shader)

            if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
                print(glGetShaderInfoLog(shader))

            program = glCreateProgram()
            glAttachShader(program, shader)
            glLinkProgram(program)

            if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
                print(glGetProgramInfoLog(program))

            glDetachShader(program, shader)
            glDeleteShader(shader)
            glUseProgram(program)
            glDeleteProgram(program)

            self._reload = False

        try:
            glUniform2f(
                glGetUniformLocation(program, "iResolution"),
                self.width() * self.window().devicePixelRatio(),
                self.height() * self.window().devicePixelRatio(),
            )
            glRecti(-1,-1, 1, 1)
        except:
            self._reload = True
            self.update()

if __name__ == '__main__':
    app = QApplication(argv)

    scrollwidget: QScrollArea = QScrollArea()
    scrollwidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    widget: QWidget = QWidget()
    widget.move(0,0)
    layout = QVBoxLayout()
    # layout.setContentsMargins(0,0,0,0)
    widget.setLayout(layout)
    for gradientWeight in ColorSpaceType:
        for gradientMix in ColorSpaceType:
            lineWidget: QWidget = QWidget()
            lineLayout: QHBoxLayout = QHBoxLayout()
            lineLayout.setContentsMargins(0,0,0,0)
            lineWidget.setLayout(lineLayout)

            label: QLabel = QLabel()
            label.setText(f'{gradientWeight.name}:{gradientMix.name}')
            label.setMinimumWidth(150)
            label.setMaximumWidth(150)
            lineWidget.layout().addWidget(label)

            gradientWidget = GradientWidget(ColorGradient(
                "Default Gradient",
                4,
                gradientWeight,
                gradientMix,
                [
                    # vec3(0.15, 0.18, 0.26),
                    # vec3(0.51, 0.56, 0.66),
                    # vec3(0.78, 0.67, 0.68),
                    # vec3(0.96, 0.75, 0.60),
                    # vec3(0.97, 0.81, 0.55),
                    # vec3(0.97, 0.61, 0.42),
                    # vec3(0.91, 0.42, 0.34),
                    # vec3(0.58, 0.23, 0.22),
                    vec3(0.02, 0.07, 0.16),
                    vec3(0.07, 0.31, 0.41),
                    vec3(0.38, 0.67, 0.69),
                    vec3(0.95, 0.85, 0.76),
                    vec3(0.98, 0.94, 0.83),
                    vec3(0.99, 0.92, 0.51),
                    vec3(0.92, 0.44, 0.40),
                    vec3(0.46, 0.25, 0.33),
                ],
                observer=Observer.TenDegreesCIE1964,
                illuminant=Illuminant.D65,
                model=FitModel.Trigonometric,
            ))
            gradientWidget.setMinimumWidth(300)
            gradientWidget.setMaximumWidth(300)
            lineWidget.layout().addWidget(gradientWidget)

            widget.layout().addWidget(lineWidget)
    # widget.setMaximumSize(400,400)
    scrollwidget.setWidget(widget)

    scrollwidget.resize(200, 400)
    scrollwidget.show()

    app.exec()
