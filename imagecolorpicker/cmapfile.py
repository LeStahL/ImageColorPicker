from typing import (
    Self,
    Optional,
)
from PyQt6.QtGui import QImage
from imagecolorpicker.colorgradient import ColorGradient
from uuid import uuid4
from pathlib import Path


class CMapFile:
    def __init__(
        self: Self,
        images: Optional[list[QImage]] = None,
        gradients: Optional[list[ColorGradient]] = None,
    ):
        self._images: list[QImage] = images or []
        self._gradients: list[ColorGradient] = gradients or []
        
    def save(self: Self, path: Path) -> dict:
        imageFiles: list[str] = []
        for image in self._images:
            imageFile: Path = path / f'{uuid4()}.jpg'
            image.save(imageFile)
            imageFiles.append(imageFile)

        return {
            'images': imageFiles,
            'gradients': list(map(
                lambda gradient: gradient.toDict(),
                self._gradients,
            )),
        }
