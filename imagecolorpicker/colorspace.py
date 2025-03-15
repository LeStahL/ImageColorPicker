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
    sqrt,
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

    # @staticmethod
    # def CIEXYZToCIELABD50(ciexyz: vec3) -> vec3:
    #     return ColorSpace.CIEXYZToCIELAB(ciexyz, ColorSpace.CIEXYZ_D50)
    
    # @staticmethod
    # def CIELABD50ToCIEXYZ(cielab: vec3) -> vec3:
    #     return ColorSpace.CIELABToCIEXYZ(cielab, ColorSpace.CIEXYZ_D50)

    # @staticmethod
    # def CIEXYZToCIELABD65(ciexyz: vec3) -> vec3:
    #     return ColorSpace.CIEXYZToCIELAB(ciexyz, ColorSpace.CIEXYZ_D65)

    # @staticmethod
    # def CIELABD65ToCIEXYZ(cielab: vec3) -> vec3:
    #     return ColorSpace.CIELABToCIEXYZ(cielab, ColorSpace.CIEXYZ_D65)
    
    # @staticmethod
    # def CIEXYZToCIELABICC(ciexyz: vec3) -> vec3:
    #     return ColorSpace.CIEXYZToCIELAB(ciexyz, ColorSpace.CIEXYZ_ICC)

    # @staticmethod
    # def CIELABICCToCIEXYZ(cielab: vec3) -> vec3:
    #     return ColorSpace.CIELABToCIEXYZ(cielab, ColorSpace.CIEXYZ_ICC)

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

    # @staticmethod
    # def CIELABToCIELCH(cielab: vec3) -> vec3:
    #     return ColorSpace.CartesianToPolar(cielab)
    
    # @staticmethod
    # def CIELCHToCIELAB(cielch: vec3) -> vec3:
    #     return ColorSpace.PolarToCartesian(cielch)
    
    @staticmethod
    def CIEXYZToOKLAB(ciexyz: vec3) -> vec3:
        return ColorSpace.OKLABM2 * pow(ColorSpace.OKLABM1 * ciexyz, vec3(3.0))
    
    @staticmethod
    def OKLABToCIEXYZ(oklab: vec3) -> vec3:
        return ColorSpace.OKLABM1Inv * pow(ColorSpace.OKLABM2Inv * oklab, vec3(3.0))

    # @staticmethod
    # def OKLABToOKLCH(oklab: vec3) -> vec3:
    #     return ColorSpace.CartesianToPolar(oklab)
    
    # @staticmethod
    # def OKLCHToOKLAB(oklch: vec3) -> vec3:
    #     return ColorSpace.PolarToCartesian(oklch)

    @staticmethod
    def CIEXYZToHunterLAB(ciexyz: vec3, whitepoint: vec3) -> vec3:
        xyz: vec3 = ciexyz / whitepoint
        ys: float = sqrt(xyz.y)
        return vec3(
            100.0 * ys,
            175.0 / 198.04 * (whitepoint.y + whitepoint.x) * (( xyz.x - xyz.y ) / ys),
            70.0 / 218.11 * (whitepoint.y + whitepoint.z) * (( xyz.y - xyz.z ) / ys),
        )
    
    @staticmethod
    def HunterLABToCIEXYZ(hunterlab: vec3, whitepoint: vec3) -> vec3:
        sk: float =  ( ( hunterlab.x / whitepoint.y ) ^ 2 ) * 100.0
        return vec3(
            (hunterlab.y / 175.0 * 198.04 * (whitepoint.y + whitepoint.x) * sqrt(sk / whitepoint.y) + sk / whitepoint.y) * whitepoint.x,
            sk,
            -(hunterlab.z / 70.0 * 218.11 * (whitepoint.y + whitepoint.z) * sqrt(sk / whitepoint.y) - sk / whitepoint.y) * whitepoint.z,
        )

