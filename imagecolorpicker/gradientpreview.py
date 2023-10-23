from typing import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import *
from OpenGL.GL import *
from sys import argv
from os.path import dirname
from imagecolorpicker import DefaultGradient, GradientWeight, GradientMix
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

    widget = GradientPreview()
    widget.show()

    app.exec()
