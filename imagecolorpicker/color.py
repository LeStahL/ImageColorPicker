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

class ColorSpaceType(IntEnum):
    RGB = 0x0
    XYZ_SRGB = 0x1
    OKLAB = 0x2
    OKLCH = 0x3
    CIEXYZ = 0x4
    CIELAB = 0x5
    CIELCH = 0x6

class ColorSpace:
    # sRGB constants
    SRGBAlpha: float = 0.055

    # CIELAB constants
    MRGBCIEXYZ: mat3 = mat3(
        0.4124564, 0.2126729, 0.0193339,
        0.3575761, 0.7151522, 0.1191920,
        0.1804375, 0.0721750, 0.9503041
    )
    MRGBCIEXYZInv: mat3 = inverse(MRGBCIEXYZ)
    CIEXYZ_D65: vec3 = vec3(95.0489, 100.0, 108.8840)
    CIEXYZ_D50: vec3 = vec3(96.4212, 100.0, 82.5188)
    CIEXYZ_ICC: vec3 = vec3(96.42, 100.0, 82.4)
    CIEDelta = 6.0 / 29.0

    # OKLAB constants
    OKLABM1: mat3 = mat3(
        0.8189330101, 0.0329845436, 0.0482003018,
        0.3618667424, 0.9293118715, 0.2643662691,
        -0.1288597137, 0.0361456387, 0.6338517070
    )
    OKLABM1Inv: mat3 = inverse(OKLABM1)
    OKLABM2: mat3 = mat3(
        0.2104542553, 1.9779984951, 0.0259040371,
        0.7936177850, -2.4285922050, 0.7827717662,
        -0.0040720468, 0.4505937099, -0.8086757660
    )
    OKLABM2Inv: mat3 = inverse(OKLABM2)

    # Based on code by tobspr, available at https://github.com/tobspr/GLSL-Color-Spaces/blob/master/ColorSpaces.inc.glsl,
    # licensed under MIT.
    @staticmethod
    def linearToSRGB(component: float) -> float:
        if component <= 0.0031308:
            return 12.92 * component
        return (1.0 + ColorSpace.SRGBAlpha) * pow(
            component,
            1. / 2.4,
        ) - ColorSpace.SRGBAlpha

    @staticmethod
    def RGBToSRGB(rgb: vec3) -> vec3:
        return vec3(
            ColorSpace.linearToSRGB(rgb.r),
            ColorSpace.linearToSRGB(rgb.g),
            ColorSpace.linearToSRGB(rgb.b),
        )
    
    @staticmethod
    def SRGBToLinear(component: float) -> float:
       if component <= 0.04045:
           return component / 12.92
       return pow(
           (component + ColorSpace.SRGBAlpha) / (1.0 + ColorSpace.SRGBAlpha),
           2.4,
        )
    
    @staticmethod
    def SRGBToRGB(srgb: vec3) -> vec3:
        return vec3(
            ColorSpace.SRGBToLinear(srgb.r),
            ColorSpace.SRGBToLinear(srgb.g),
            ColorSpace.SRGBToLinear(srgb.b),
        )
    
    # Based on info at https://www.image-engineering.de/library/technotes/958-how-to-convert-between-srgb-and-ciexyz
    # and https://www.easyrgb.com/en/math.php
    @staticmethod
    def RGBToCIEXYZ(rgb: vec3) -> vec3:
        return ColorSpace.MRGBCIEXYZ * rgb
    
    @staticmethod
    def CIEXYZToRGB(xyz: vec3) -> vec3:
        return ColorSpace.MRGBCIEXYZInv * xyz

    # This is equivalent to info available at https://www.easyrgb.com/en/math.php
    @staticmethod
    def g(component: float) -> float:
        if component > pow(ColorSpace.CIEDelta, 3.0):
            return pow(component, 1.0 / 3.0)
        return component / 3. / pow(ColorSpace.CIEDelta, 2.0) + 4.0 / 29.0
    
    @staticmethod
    def ginv(component: float) -> float:
        if component > ColorSpace.CIEDelta:
            return pow(component, 3.0)
        return 3.0 * pow(ColorSpace.CIEDelta, 2.0) * (component - 4.0 / 29.0)

    @staticmethod
    def CIEXYZToCIELAB(ciexyz: vec3, whitepoint: vec3) -> vec3:
        xyz: vec3 = ciexyz / whitepoint
        gy: float = ColorSpace.g(xyz.y)
        return vec3(
            116.0 * gy - 16.0,
            500.0 * (ColorSpace.g(xyz.x) - gy),
            200.0 * (gy - ColorSpace.g(xyz.z)),
        )

    @staticmethod
    def CIELABToCIEXYZ(cielab: vec3, whitepoint: vec3) -> vec3:
        l16: float = (cielab.x + 16.0) / 116.0
        return whitepoint * vec3(
            ColorSpace.ginv(l16 + cielab.y / 500.0),
            ColorSpace.ginv(l16),
            ColorSpace.ginv(l16 - cielab.z),
        )

    @staticmethod
    def CIEXYZToCIELABD50(ciexyz: vec3) -> vec3:
        return ColorSpace.CIEXYZToCIELAB(ciexyz, ColorSpace.CIEXYZ_D50)
    
    @staticmethod
    def CIELABD50ToCIEXYZ(cielab: vec3) -> vec3:
        return ColorSpace.CIELABToCIEXYZ(cielab, ColorSpace.CIEXYZ_D50)

    @staticmethod
    def CIEXYZToCIELABD65(ciexyz: vec3) -> vec3:
        return ColorSpace.CIEXYZToCIELAB(ciexyz, ColorSpace.CIEXYZ_D65)

    @staticmethod
    def CIELABD65ToCIEXYZ(cielab: vec3) -> vec3:
        return ColorSpace.CIELABToCIEXYZ(cielab, ColorSpace.CIEXYZ_D65)
    
    @staticmethod
    def CIEXYZToCIELABICC(ciexyz: vec3) -> vec3:
        return ColorSpace.CIEXYZToCIELAB(ciexyz, ColorSpace.CIEXYZ_ICC)

    @staticmethod
    def CIELABICCToCIEXYZ(cielab: vec3) -> vec3:
        return ColorSpace.CIELABToCIEXYZ(cielab, ColorSpace.CIEXYZ_ICC)

    @staticmethod
    def CartesianToPolar(lab: vec3) -> vec3:
        return vec3(
            lab.x,
            length(lab.yz),
            atan(lab.z, lab.y),
        )

    @staticmethod
    def PolarToCartesian(lch: vec3) -> vec3:
        return vec3(
            lch.x,
            lch.y * cos(lch.z),
            lch.y * sin(lch.z),
        )

    @staticmethod
    def CIELABToCIELCH(cielab: vec3) -> vec3:
        return ColorSpace.CartesianToPolar(cielab)
    
    @staticmethod
    def CIELCHToCIELAB(cielch: vec3) -> vec3:
        return ColorSpace.PolarToCartesian(cielch)
    
    @staticmethod
    def CIEXYZToOKLAB(ciexyz: vec3) -> vec3:
        return ColorSpace.OKLABM2 * pow(ColorSpace.OKLABM1 * ciexyz, vec3(3.0))
    
    @staticmethod
    def OKLABToCIEXYZ(oklab: vec3) -> vec3:
        return ColorSpace.OKLABM1Inv * pow(ColorSpace.OKLABM2Inv * oklab, vec3(3.0))

    @staticmethod
    def OKLABToOKLCH(oklab: vec3) -> vec3:
        return ColorSpace.CartesianToPolar(oklab)
    
    @staticmethod
    def OKLCHToOKLAB(oklch: vec3) -> vec3:
        return ColorSpace.PolarToCartesian(oklch)

    



class Color:
    Msrgb: mat3 = mat3(
        0.4124564, 0.2126729, 0.0193339,
        0.3575761, 0.7151522, 0.1191920,
        0.1804375, 0.0721750, 0.9503041
    )
    MsrgbInv: mat3 = inverse(Msrgb)
    M1: mat3 = mat3(
        0.8189330101, 0.0329845436, 0.0482003018,
        0.3618667424, 0.9293118715, 0.2643662691,
        -0.1288597137, 0.0361456387, 0.6338517070
    )
    M1Inv: mat3 = inverse(M1)
    M2: mat3 = mat3(
        0.2104542553, 1.9779984951, 0.0259040371,
        0.7936177850, -2.4285922050, 0.7827717662,
        -0.0040720468, 0.4505937099, -0.8086757660
    )
    M2Inv: mat3 = inverse(M2)
    MCIEXYZ: mat3 = mat3(
        .49, .17697, .0,
        .31, .8124, .01,
        .2, .01063, .99
    )
    MCIEXYZinv: mat3 = inverse(MCIEXYZ)
    CIEXYZ_D65: vec3 = vec3(95.0489, 100., 108.8840)
    CIEXYZ_D50: vec3 = vec3(96.4212, 100., 82.5188)
    WhitePoint: vec3 = CIEXYZ_D50
    delta: float = 6. / 29.
    ConversionOrder: List[ColorSpace] = [
        ColorSpace.CIELCH,
        ColorSpace.CIELAB,
        ColorSpace.CIEXYZ,
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

    @staticmethod
    def g(x: float) -> float:
        return pow(x, 1. / 3.) if x > pow(Color.delta, 3.) else (x / 3. / pow(Color.delta, 2.) + 4. / 29.)

    @staticmethod
    def ginv(x: float) -> float:
        return pow(x, 3.) if x > Color.delta else (3. * pow(Color.delta, 2.) * (x - 4. / 29.))

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
            elif origin == ColorSpace.RGB and target == ColorSpace.CIEXYZ:
                self._color = Color.MCIEXYZ * self._color
            elif origin == ColorSpace.CIEXYZ and target == ColorSpace.RGB:
                self._color = Color.MCIEXYZinv * self._color
            elif origin == ColorSpace.CIEXYZ and target == ColorSpace.CIELAB:
                self._color = self._color / Color.WhitePoint
                gy: float = Color.g(self._color.y)
                self._color = vec3(
                    116. * gy - 16.,
                    500. * (Color.g(self._color.x) - gy),
                    200. * (gy - Color.g(self._color.z)),
                )
            elif origin == ColorSpace.CIELAB and target == ColorSpace.CIEXYZ:
                l16: float = (self._color.x + 16.) / 116.
                self._color = Color.WhitePoint * vec3(
                    Color.ginv(l16 + self._color.y / 500.),
                    Color.ginv(l16),
                    Color.ginv(l16 - self._color.z / 200.),
                )
            elif origin == ColorSpace.CIELAB and target == ColorSpace.CIELCH:
                self._color = vec3(self._color.x, length(self._color.yz), atan(self._color.z, self._color.y))
            elif origin == ColorSpace.CIELCH and target == ColorSpace.CIELAB:
                self._color = vec3(self._color.x, self._color.y * vec2(cos(self._color.z), sin(self._color.z)))

        self._space = space

    def __repr__(self) -> str:
        return 'vec3({:.2f}, {:.2f}, {:.2f})'.format(*self._color.to_tuple())

    @staticmethod
    def distance(c1: Self, c2: Self) -> float:
        return length(c2._color - c1._color)
    
    @staticmethod
    def mix(c1: Self, c2: Self, amount: float) -> Self:
        result = deepcopy(c1)
        result._color = mix(c1._color, c2._color, amount)
        return result

    def toList(self: Self) -> List[float]:
        return [self._color.x, self._color.y, self._color.z]
