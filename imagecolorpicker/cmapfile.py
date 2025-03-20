from typing import (
    Self,
    Optional,
)
from PyQt6.QtGui import QImage
from imagecolorpicker.colorgradient import ColorGradient
from uuid import uuid4
from pathlib import Path
from imagecolorpicker.colorspace import ColorSpaceType
from rtoml import (
    loads,
    dumps,
)

class CMapFile:
    DefaultPreviewColorSpaces: list[list[ColorSpaceType]] = [
        [ColorSpaceType.SRGB, ColorSpaceType.SRGB],
        [ColorSpaceType.RGB, ColorSpaceType.RGB],
        [ColorSpaceType.OKLAB, ColorSpaceType.OKLAB],
        [ColorSpaceType.CIELAB, ColorSpaceType.CIELAB],
    ]

    def __init__(
        self: Self,
        images: Optional[list[QImage]] = None,
        gradients: Optional[list[ColorGradient]] = None,
        previewColorSpaces: Optional[list[list[ColorSpaceType]]] = None,
    ):
        self._images: list[QImage] = images or []
        self._gradients: list[ColorGradient] = gradients or []
        self._previewColorSpaces: list[list[ColorSpaceType]] = previewColorSpaces or CMapFile.DefaultPreviewColorSpaces
        
    def save(self: Self, path: Path) -> None:
        imageFiles: list[str] = []
        for image in self._images:
            imageFile: str = str(path / f'{uuid4()}.jpg')
            image.save(imageFile)
            imageFiles.append(imageFile)

        (path / 'cmap.toml').write_text(dumps({
            'images': imageFiles,
            'gradients': list(map(
                lambda gradient: gradient.toDict(),
                self._gradients,
            )),
            'preview_color_spaces': list(map(
                lambda pair: {
                    'weight': pair[0].name,
                    'mix': pair[1].name,
                },
                self._previewColorSpaces,
            ))
        }, pretty=True))

    def load(self: Self, path: Path) -> None:
        if path.is_file():
            path = path.parent

        info = loads((path / 'cmap.toml').read_text())
        self._images = list(map(
            lambda imageFile: QImage(str(path / imageFile)),
            info['images'],
        ))
        self._gradients = list(map(
            lambda gradientInfo: ColorGradient.fromDict(gradientInfo),
            info['gradients'],
        ))
