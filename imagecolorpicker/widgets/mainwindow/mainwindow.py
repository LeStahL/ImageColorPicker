from enum import (
    IntEnum,
    auto,
)
from importlib.resources import files
import imagecolorpicker
from .ui_mainwindow import Ui_MainWindow
from PyQt6.QtCore import (
    pyqtSignal,
    Qt,
    QUrl,
    QPointF,
)
from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QMessageBox,
    QApplication,
)
from PyQt6.QtGui import (
    QIcon,
    QGuiApplication,
    QColor,
)
from typing import (
    Self,
    Optional,
)


class CoordinateType(IntEnum):
    AspectCorrectedBottomUp = auto()
    NormalizedBottomUp = auto()
    NormalizedTopDown = auto()


class MainWindow(QMainWindow):
    quitRequested: pyqtSignal = pyqtSignal()

    UIFile = "mainwindow.ui"
    
    def __init__(
        self: Self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Window,
    ) -> None:
        super().__init__(parent, flags)

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.setWindowIcon(QIcon(str(files(imagecolorpicker) / 'team210.ico')))

        self._coordinateType: CoordinateType = CoordinateType.AspectCorrectedBottomUp
        self._ui.actionAspect_Corrected_Top_Down.triggered.connect(lambda: self._updateCoordinateType(CoordinateType.AspectCorrectedBottomUp))
        self._ui.actionNormalized_Bottom_Up.triggered.connect(lambda: self._updateCoordinateType(CoordinateType.NormalizedBottomUp))
        self._ui.actionNormalized_Top_Down.triggered.connect(lambda: self._updateCoordinateType(CoordinateType.NormalizedTopDown))
 
        # self.tabifyDockWidget(self._ui.gradientPreviewDockWidget, self._ui.gradientListDockWidget)
        self.tabifyDockWidget(self._ui.gradientPropertyDockWidget, self._ui.gradientColorDockWidget)

        self._ui.picker.hovered.connect(lambda cursor: self.statusBar().showMessage('Position: x = {}, y = {}'.format(*self._coordinates(cursor.x(), cursor.y()))))
        self._ui.picker.picked.connect(self._updatePickInformation)
        self._ui.actionQuit.triggered.connect(lambda: QApplication.exit(0))
        self._ui.actionPaste.triggered.connect(self.paste)
        self._ui.actionAbout.triggered.connect(self.about)

        self._ui.actionForce_16_9_View.triggered.connect(self._force16_9View)

        self._ui.actionAbout_Qt.triggered.connect(self.aboutQt)

    def _updateCoordinateType(self: Self, coordinateType: CoordinateType) -> None:
        self._coordinateType = coordinateType
        self._ui.actionAspect_Corrected_Top_Down.setChecked(coordinateType == CoordinateType.AspectCorrectedBottomUp)
        self._ui.actionNormalized_Bottom_Up.setChecked(coordinateType == CoordinateType.NormalizedBottomUp)
        self._ui.actionNormalized_Top_Down.setChecked(coordinateType == CoordinateType.NormalizedTopDown)

    def _force16_9View(self: Self) -> None:
        w = self._ui.picker.width()
        h = int(9. / 16. * w)
        self._ui.picker.resize(w, h)

    def _coordinates(self: Self, qtX: float, qtY: float) -> tuple[float, float]:
        if self._coordinateType == CoordinateType.NormalizedTopDown:
            return qtX, qtY
        qtY = 1. - qtY
        if self._coordinateType == CoordinateType.NormalizedBottomUp:
            return qtX, qtY
        width: int = self._ui.picker.rect().width()
        height: int = self._ui.picker.rect().height()
        return (qtX - .5) * width / height, (qtY - .5) * height / height

    def _updatePickInformation(self: Self, cursor: QPointF, color: QColor) -> None:
        self._ui.colorLabel.setStyleSheet('background-color:{}'.format(color.name()))

    def paste(self: Self) -> None:
        clipboard = QGuiApplication.clipboard()

        if clipboard.mimeData().hasImage():
            self._ui.picker.setImage(clipboard.image())
        if clipboard.mimeData().hasHtml():
            self._ui.picker.loadFromHTML(clipboard.mimeData().html())
        if clipboard.mimeData().hasUrls():
            if len(clipboard.mimeData().urls()) == 0:
                return

            # Only load first URL.
            url: QUrl = clipboard.mimeData().urls()[0]
            self._ui.picker.loadFromUrl(url)

        # Yeah I know.
        self._ui.picker.imageChanged.emit(self._ui.picker._image)

    def about(self: Self) -> None:
        aboutMessage = QMessageBox()
        aboutMessage.setWindowIcon(QIcon(str(files(imagecolorpicker) / 'team210.ico')))
        aboutMessage.setText("Image Color Picker is GPLv3 and (c) 2023 Alexander Kraus <nr4@z10.info>.")
        aboutMessage.setWindowTitle("About Image Color Picker")
        aboutMessage.setIcon(QMessageBox.Icon.Information)
        aboutMessage.exec()

    def aboutQt(self: Self) -> None:
        QMessageBox.aboutQt(self, "About Qt...")
