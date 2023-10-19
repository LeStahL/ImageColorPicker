from typing import *
from PyQt6 import QtGui
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import *
from OpenGL.GL import *
from sys import argv
from os.path import (
    join,
    dirname,
)
from imagecolorpicker import DefaultGradient, ColorGradient, GradientWeight, GradientMix
from copy import deepcopy
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
        self._shader = None
        self._program = None

        self._environment = Environment(
            loader=FileSystemLoader(dirname(__file__)),
            autoescape=select_autoescape(),
        )
        self._template = self._environment.get_template(GradientPreview.ShaderFile)

    def changeColorMaps(self: Self, colorMaps: List[Tuple[GradientWeight, GradientMix, List[vec3]]]) -> None:
        self._colorMaps = colorMaps
        self._reload = True
        self.update()

    def resizeGL(self: Self, w: int, h: int) -> None:
        w = int(w * self.window().devicePixelRatio())
        h = int(h * self.window().devicePixelRatio())

        if self._shader != None:
            glViewport(0, 0, w, h)
            glUniform2f(self._resolutionLocation, w, h)
        self.update()

    def paintGL(self: Self) -> None:
        if self._reload:
            if self._shader is not None:
                glDetachShader(self._program, self._shader)
                glDeleteShader(self._shader)

            if self._program is not None:
                glUseProgram(0)
                glDeleteProgram(self._program)

            self._shader = glCreateShader(GL_FRAGMENT_SHADER)
            self._source = self._template.render(colorMaps=self._colorMaps)
            glShaderSource(self._shader, self._source)
            glCompileShader(self._shader)

            if glGetShaderiv(self._shader, GL_COMPILE_STATUS) != GL_TRUE:
                print(glGetShaderInfoLog(self._shader))

            self._program = glCreateProgram()
            glAttachShader(self._program, self._shader)
            glLinkProgram(self._program)

            if glGetProgramiv(self._program, GL_LINK_STATUS) != GL_TRUE:
                print(glGetProgramInfoLog(self._program))

            glUseProgram(self._program)
            self._resolutionLocation = glGetUniformLocation(self._program, "iResolution")
            glUniform2f(self._resolutionLocation, self.width() * self.window().devicePixelRatio(), self.height() * self.window().devicePixelRatio())

            self._reload = False

        glRecti(-1,-1, 1, 1)

if __name__ == '__main__':
    app = QApplication(argv)

    widget = GradientPreview()
    widget.show()

    app.exec()
