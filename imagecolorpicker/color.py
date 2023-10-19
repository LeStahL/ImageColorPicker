from glm import (
    mat3,
    vec3,
    vec2,
    inverse,
    pow,
    length,
    atan,
    sin,
    cos,
    mix,
)
from typing import (
    Self,
    List,
)
from enum import IntEnum
from copy import deepcopy

class ColorSpace(IntEnum):
    RGB = 0x0
    XYZ_SRGB = 0x1
    OKLAB = 0x2
    OKLCH = 0x3

class Color:
    Msrgb = mat3(
        0.4124564, 0.2126729, 0.0193339,
        0.3575761, 0.7151522, 0.1191920,
        0.1804375, 0.0721750, 0.9503041
    )
    MsrgbInv = inverse(Msrgb)
    M1 = mat3(
        0.8189330101, 0.0329845436, 0.0482003018,
        0.3618667424, 0.9293118715, 0.2643662691,
        -0.1288597137, 0.0361456387, 0.6338517070
    )
    M1Inv = inverse(M1)
    M2 = mat3(
        0.2104542553, 1.9779984951, 0.0259040371,
        0.7936177850, -2.4285922050, 0.7827717662,
        -0.0040720468, 0.4505937099, -0.8086757660
    )
    M2Inv = inverse(M2)
    ConversionOrder = [
        ColorSpace.RGB,
        ColorSpace.XYZ_SRGB,
        ColorSpace.OKLAB,
        ColorSpace.OKLCH,
    ]

    def __init__(
        self: Self,
        red: float = 0.0,
        green: float = 0.0,
        blue: float = 0.0,
        space: ColorSpace = ColorSpace.RGB,
    ) -> None:
        self._color: vec3 = vec3(red, green, blue)
        self._space: ColorSpace = space

    def toColorSpace(self: Self, space: ColorSpace) -> None:
        startIndex: int = Color.ConversionOrder.index(self._space)
        endIndex: int = Color.ConversionOrder.index(space)
        searchRange: List[int] = list(range(min(startIndex, endIndex), max(startIndex, endIndex)))
        if startIndex > endIndex:
            searchRange.append(startIndex)
            searchRange = list(reversed(searchRange))
        else:
            searchRange.append(endIndex)

        for orderIndex in range(len(searchRange) - 1):
            index = searchRange[orderIndex]
            nextIndex = searchRange[orderIndex + 1]
            origin: ColorSpace = Color.ConversionOrder[index]
            target: ColorSpace = Color.ConversionOrder[nextIndex]

            if origin == ColorSpace.RGB and target == ColorSpace.XYZ_SRGB:
                self._color = Color.Msrgb * self._color
            elif origin == ColorSpace.XYZ_SRGB and target == ColorSpace.RGB:
                self._color = Color.MsrgbInv * self._color
            elif origin == ColorSpace.XYZ_SRGB and target == ColorSpace.OKLAB:
                self._color = Color.M2 * pow(Color.M1 * self._color, vec3(1.0/3.0))
            elif origin == ColorSpace.OKLAB and target == ColorSpace.XYZ_SRGB:
                self._color = Color.M1Inv * pow(Color.M2Inv * self._color, vec3(3.0))
            elif origin == ColorSpace.OKLAB and target == ColorSpace.OKLCH:
                self._color = vec3(self._color.x, length(self._color.yz), atan(self._color.z, self._color.y))
            elif origin == ColorSpace.OKLCH and target == ColorSpace.OKLAB:
                self._color = vec3(self._color.x, self._color.y * vec2(cos(self._color.z), sin(self._color.z)))

        self._space = space

    def __repr__(self) -> str:
        return self._color.__repr__().replace('vec3', 'Color')

    @staticmethod
    def distance(c1: Self, c2: Self) -> float:
        return length(c2._color - c1._color)
    
    @staticmethod
    def mix(c1: Self, c2: Self, amount: float) -> Self:
        result = deepcopy(c1)
        result._color = mix(c1._color, c2._color, amount)
        return result
