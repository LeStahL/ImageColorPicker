from typing import (
    Self,
    Optional,
)
from PyQt6.QtGui import QImage
from imagecolorpicker.colorgradient import ColorGradient
from pathlib import Path
from imagecolorpicker.colorspace import ColorSpaceType
from rtoml import (
    loads,
    dumps,
)
from hashlib import md5

class CMapFile:
    DefaultPreviewColorSpaces: list[list[ColorSpaceType]] = [
        [ColorSpaceType.SRGB, ColorSpaceType.SRGB],
        [ColorSpaceType.OKLAB, ColorSpaceType.OKLAB],
        [ColorSpaceType.CIELAB, ColorSpaceType.CIELAB],
        [ColorSpaceType.ACESAP1, ColorSpaceType.ACESAP1],
        [ColorSpaceType.HunterLCH, ColorSpaceType.HunterLCH],
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
            # image.bits()
            ptr = image.bits()
            ptr.setsize(image.sizeInBytes())
            
            imageFile: str = str(path.parent / f'{md5(ptr.asstring()).hexdigest()}.jpg')
            print(imageFile)
            image.save(imageFile)
            imageFiles.append(imageFile)

        path.write_text(dumps({
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
        info = loads(path.read_text())
        self._images = list(map(
            lambda imageFile: QImage(str(path.parent / imageFile)),
            info['images'],
        ))
        self._gradients = list(map(
            lambda gradientInfo: ColorGradient.fromDict(gradientInfo),
            info['gradients'],
        ))
        self._previewColorSpaces = list(map(
            lambda previewInfo: [ColorSpaceType[previewInfo['weight']], ColorSpaceType[previewInfo['mix']]],
            info['preview_color_spaces'],
        ))
