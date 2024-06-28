from typing import *
from PyQt6 import QtGui
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkReply,
)
from sys import argv
from os.path import (
    join,
    dirname,
)
from bs4 import BeautifulSoup
from base64 import b64decode
from traceback import print_exc
from requests import get

class PickableColorLabel(QWidget):
    DefaultImage = 'default.png'
    CursorSize = 0.05

    picked = pyqtSignal(QPointF, QColor)
    hovered = pyqtSignal(QPointF)
    rightClicked = pyqtSignal(QPointF, QColor)

    def __init__(
        self: Self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Widget,
    ) -> None:
        super().__init__(parent, flags)

        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self._image: QImage = QImage(join(dirname(__file__), PickableColorLabel.DefaultImage))
        self._cursor: QPointF = QPointF(0., 0.)
        self._color: QColor = QColor()
        self._picking: bool = False

        self._networkManager: QNetworkAccessManager = QNetworkAccessManager()

    @property
    def components(self: Self) -> Tuple[float]:
        return self._color.redF(), self._color.greenF(), self._color.blueF()

    def paintEvent(self: Self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)

        if a0 is None:
            return
        
        contrastColor: Qt.GlobalColor = Qt.GlobalColor.black if 0.299 * self._color.red() + 0.587 * self._color.green() + 0.114 * self._color.blue() > 186.0 else Qt.GlobalColor.white
        
        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawImage(a0.rect(), self._image, self._image.rect())        
        pen: QPen = painter.pen()
        pen.setWidthF(1.0)
        pen.setColor(contrastColor)
        painter.setPen(pen)
        
        size: QSizeF = a0.rect().size().toSizeF()
        absolutePosition: QPointF = QPointF(self._cursor.x() * size.width(), self._cursor.y() * size.height())
        absoluteCursorSize: float = PickableColorLabel.CursorSize * size.height()
        painter.drawLine(absolutePosition + QPointF(-absoluteCursorSize, 0), absolutePosition + QPointF(absoluteCursorSize, 0))
        painter.drawLine(absolutePosition + QPointF(0, -absoluteCursorSize), absolutePosition + QPointF(0, absoluteCursorSize))
        painter.drawEllipse(QRectF(absolutePosition - .5 * QPointF(absoluteCursorSize, absoluteCursorSize) - QPointF(2.,2.), QSizeF(absoluteCursorSize + 4., absoluteCursorSize + 4.)))
        painter.drawEllipse(QRectF(absolutePosition - .5 * QPointF(absoluteCursorSize, absoluteCursorSize) + QPointF(2.,2.), QSizeF(absoluteCursorSize - 4., absoluteCursorSize - 4.)))
        
        pen: QPen = painter.pen()
        pen.setWidthF(4)
        pen.setColor(self._color)
        painter.setPen(pen)
        painter.drawEllipse(QRectF(absolutePosition - .5 * QPointF(absoluteCursorSize, absoluteCursorSize), QSizeF(absoluteCursorSize, absoluteCursorSize)))

    def mousePressEvent(self: Self, a0: Optional[QMouseEvent]) -> None:
        super().mousePressEvent(a0)
        self._picking = True
        self._pick(a0)

    def mouseReleaseEvent(self: Self, a0: Optional[QMouseEvent]) -> None:
        super().mousePressEvent(a0)
        self._picking = False

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        super().mouseMoveEvent(a0)
        if self._picking:
            self._pick(a0)
        self._hover(a0)

    def _hover(self: Self, a0: Optional[QMouseEvent]) -> None:
        if a0 is None:
            return
        
        absolutePosition = a0.position()
        size = self.size().toSizeF()
        relativePosition = QPointF(absolutePosition.x() / size.width(), absolutePosition.y() / size.height())
        
        self.hovered.emit(relativePosition)

    def _pick(self: Self, a0: Optional[QMouseEvent]) -> None:
        if a0 is None:
            return
        
        absolutePosition: QPointF = a0.position()
        size: QSizeF = self.size().toSizeF()
        relativePosition: QPointF = QPointF(absolutePosition.x() / size.width(), absolutePosition.y() / size.height())
        imageSize: QSizeF = self._image.size().toSizeF()
        absoluteImagePosition: QPoint = QPointF(relativePosition.x() * imageSize.width(), relativePosition.y() * imageSize.height()).toPoint()
        
        self._cursor = relativePosition
        self._color = self._image.pixelColor(absoluteImagePosition)
        self.picked.emit(self._cursor, self._color)

        self.update()

    def setImage(self: Self, image: QImage) -> None:
        self._image = image
        self.update()

    def dragEnterEvent(self: Self, a0: QDragEnterEvent) -> None:
        super().dragEnterEvent(a0)

        # print(a0.mimeData().formats())

        if True in [
            a0.mimeData().hasImage(),
            a0.mimeData().hasHtml(),
            a0.mimeData().hasUrls(),
        ]:
            a0.acceptProposedAction()

    def dropEvent(self: Self, a0: QDropEvent) -> None:
        super().dropEvent(a0)

        if a0.mimeData().hasImage():
            self.setImage(a0.mimeData().imageData())
        elif a0.mimeData().hasHtml():
            self.loadFromHTML(a0.mimeData().html())
        elif a0.mimeData().hasUrls():
            if len(a0.mimeData().urls()) == 0:
                return

            # Only load first URL.
            url: QUrl = a0.mimeData().urls()[0]
            self.loadFromUrl(url)

    def loadFromUrl(self: Self, url: QUrl) -> None:
        request: QNetworkRequest = QNetworkRequest(url)
        reply: QNetworkReply = self._networkManager.get(request)
        result: bytes = reply.readAll()

        self.loadFromBinary(result)

    def loadFromHTML(self: Self, html: str) -> None:
        try:
            html = BeautifulSoup(
                html,
                features='html.parser',
            )
            imgTags = html.findAll('img')
            if len(imgTags) != 0:
                src: str = imgTags[0]['src']
                pixmap = QPixmap()
                if src.startswith('data:image/png;base64,'):
                    src = src.replace('data:image/png;base64,', '')
                    pixmap.loadFromData(b64decode(src))
                elif src.startswith('data:image/jpeg;base64,'):
                    src = src.replace('data:image/jpeg;base64,', '')
                    pixmap.loadFromData(b64decode(src))
                else:
                    response = get(src)
                    pixmap.loadFromData(response.content)
                self.setImage(pixmap.toImage())
        except:
            print_exc()
            print("Attempted to load unsupported html.")

    def loadFromBinary(self: Self, binary: bytes) -> None:
        try:
            pixmap = QPixmap()
            pixmap.loadFromData(binary)
            self.setImage(pixmap.toImage())
        except:
            print_exc()
            print("Attempted to load unsupported image binary.")
