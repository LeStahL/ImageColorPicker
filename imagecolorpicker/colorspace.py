from glm import (
    mat3,
    vec3,
    vec2,
    vec4,
    inverse,
    pow,
    length,
    atan,
    sin,
    cos,
    mix,
    sqrt,
    fract,
    clamp,
    dot,
)
from typing import (
    Self,
    List,
    Callable,
)
from enum import (
    IntEnum,
    IntFlag,
    auto,
)
from copy import deepcopy
from networkx import (
    DiGraph,
    shortest_path,
    draw,
    spring_layout,
)

class ColorSpaceType(IntEnum):
    SRGB = 0x0
    RGB = 0x1
    CIEXYZ = 0x2
    CIELAB = 0x3
    CIELCH = 0x4
    OKLAB = 0x5
    OKLCH = 0x6
    HunterLAB = 0x7
    HunterLCH = 0x8
    HSL = 0x9
    YCbCr = 0xA
    CIE1931Yxy = 0xB
    HSV = 0xC
    CIELuv = 0xD
    AdobeRGB = 0xE
    ACESAP1 = 0xF

class ColorSpaceParameterType(IntFlag):
    NoParameters = 0x0
    Illuminant = auto()
    Observer = auto()

class Observer(IntEnum):
    TwoDegreesCIE1931 = auto()
    TenDegreesCIE1964 = auto()

class Illuminant(IntEnum):
    A = auto()
    B = auto()
    C = auto()
    D50 = auto()
    D55 = auto()
    D65 = auto()
    D75 = auto()
    E = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()
    F4 = auto()
    F5 = auto()
    F6 = auto()
    F7 = auto()
    F8 = auto()
    F9 = auto()
    F10 = auto()
    F11 = auto()
    F12 = auto()

class ColorSpace:
    # Tristimuli
    Tristimuli: dict[Observer, dict[Illuminant, vec3]] = {
        Observer.TwoDegreesCIE1931: {
            Illuminant.A: vec3(109.850, 100.000, 35.585),
            Illuminant.B: vec3(99.0927, 100.000, 85.313),
            Illuminant.C: vec3(98.074, 100.000, 118.232),
            Illuminant.D50: vec3(96.422, 100.000, 82.521),
            Illuminant.D55: vec3(95.682, 100.000, 92.149),
            Illuminant.D65: vec3(95.047, 100.000, 108.883),
            Illuminant.D75: vec3(94.972, 100.000, 122.638),
            Illuminant.E: vec3(100.000, 100.000, 100.000),
            Illuminant.F1: vec3(92.834, 100.000, 103.665),
            Illuminant.F2: vec3(99.187, 100.000, 67.395),
            Illuminant.F3: vec3(103.754, 100.000, 49.861),
            Illuminant.F4: vec3(109.147, 100.000, 38.813),
            Illuminant.F5: vec3(90.872, 100.000, 98.723),
            Illuminant.F6: vec3(97.309, 100.000, 60.191),
            Illuminant.F7: vec3(95.044, 100.000, 108.755),
            Illuminant.F8: vec3(96.413, 100.000, 82.333),
            Illuminant.F9: vec3(100.365, 100.000, 67.868),
            Illuminant.F10: vec3(96.174, 100.000, 81.712),
            Illuminant.F11: vec3(100.966, 100.000, 64.370),
            Illuminant.F12: vec3(108.046, 100.000, 39.228),
        },
        Observer.TenDegreesCIE1964: {
            Illuminant.A: vec3(111.144, 100.000, 35.200),
            Illuminant.B: vec3(99.178, 100.000, 84.3493),
            Illuminant.C: vec3(97.285, 100.000, 116.145),
            Illuminant.D50: vec3(96.720, 100.000, 81.427),
            Illuminant.D55: vec3(95.799, 100.000, 90.926),
            Illuminant.D65: vec3(94.811, 100.000, 107.304),
            Illuminant.D75: vec3(94.416, 100.000, 120.641),
            Illuminant.E: vec3(100.000, 100.000, 100.000),
            Illuminant.F1: vec3(94.791, 100.000, 103.191),
            Illuminant.F2: vec3(103.280, 100.000, 69.026),
            Illuminant.F3: vec3(108.968, 100.000, 51.965),
            Illuminant.F4: vec3(114.961, 100.000, 40.963),
            Illuminant.F5: vec3(93.369, 100.000, 98.636),
            Illuminant.F6: vec3(102.148, 100.000, 62.074),
            Illuminant.F7: vec3(95.792, 100.000, 107.687),
            Illuminant.F8: vec3(97.115, 100.000, 81.135),
            Illuminant.F9: vec3(102.116, 100.000, 67.826),
            Illuminant.F10: vec3(99.001, 100.000, 83.134),
            Illuminant.F11: vec3(103.866, 100.000, 65.627),
            Illuminant.F12: vec3(111.428, 100.000, 40.353),
        },
    }

    # sRGB constants
    SRGBAlpha: float = 0.055

    # CIELAB constants
    MRGBCIEXYZ: mat3 = mat3(
        0.4124564, 0.2126729, 0.0193339,
        0.3575761, 0.7151522, 0.1191920,
        0.1804375, 0.0721750, 0.9503041
    )
    MRGBCIEXYZInv: mat3 = inverse(MRGBCIEXYZ)
    # CIEXYZ_D65: vec3 = vec3(95.0489, 100.0, 108.8840)
    # CIEXYZ_D50: vec3 = vec3(96.4212, 100.0, 82.5188)
    # CIEXYZ_ICC: vec3 = vec3(96.42, 100.0, 82.4)
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

    MACESAPMInv: mat3 = mat3(
        1.6410233797, -0.3248032942, -0.2364246952,
        -0.6636628587,  1.6153315917,  0.0167563477,
        0.0117218943, -0.0082844420,  0.9883948585,
    )
    MACESAPM: mat3 = inverse(MACESAPMInv)

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
        var_X = ciexyz.x / whitepoint.x
        var_Y = ciexyz.y / whitepoint.y
        var_Z = ciexyz.z / whitepoint.z
        if var_X > 0.008856:
            var_X = pow(var_X, 1 / 3)
        else:
            var_X = 7.787 * var_X + 16 / 116
        if var_Y > 0.008856:
            var_Y = pow(var_Y, 1 / 3)
        else:
            var_Y = 7.787 * var_Y + 16 / 116
        if var_Z > 0.008856:
            var_Z = pow(var_Z, 1 / 3)
        else:
            var_Z = 7.787 * var_Z + 16 / 116

        return vec3(
            116 * var_Y - 16,
            500 * (var_X - var_Y),
            200 * (var_Y - var_Z),
        )

    @staticmethod
    def CIELABToCIEXYZ(cielab: vec3, whitepoint: vec3) -> vec3:
        var_Y = (cielab.x + 16) / 116
        var_X = cielab.y / 500 + var_Y
        var_Z = var_Y - cielab.z / 200

        if pow(var_Y, 3) > 0.008856:
            var_Y = pow(var_Y, 3)
        else:
            var_Y = (var_Y - 16 / 116) / 7.787
        if pow(var_X, 3) > 0.008856:
            var_X = pow(var_X, 3)
        else:
            var_X = (var_X - 16 / 116) / 7.787
        if pow(var_Z, 3) > 0.008856:
            var_Z = pow(var_Z, 3)
        else:
            var_Z = (var_Z - 16 / 116) / 7.787

        return vec3(
            var_X,
            var_Y,
            var_Z,
        ) * whitepoint

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
    def CIEXYZToOKLAB(ciexyz: vec3) -> vec3:
        return ColorSpace.OKLABM2 * pow(ColorSpace.OKLABM1 * ciexyz, vec3(1. / 3.))
    
    @staticmethod
    def OKLABToCIEXYZ(oklab: vec3) -> vec3:
        return ColorSpace.OKLABM1Inv * pow(ColorSpace.OKLABM2Inv * oklab, vec3(3.0))

    @staticmethod
    def CIEXYZToHunterLAB(ciexyz: vec3, whitepoint: vec3) -> vec3:
        var_Ka = 175.0 / 198.04 * (whitepoint.y + whitepoint.x)
        var_Kb = 70.0 / 218.11 * (whitepoint.y + whitepoint.z)

        return vec3(
            100.0 * sqrt(ciexyz.y / whitepoint.y),
            var_Ka * (ciexyz.x / whitepoint.x - ciexyz.y / whitepoint.y) / sqrt(ciexyz.y / whitepoint.y),
            var_Kb * (ciexyz.y / whitepoint.y - ciexyz.z / whitepoint.z) / sqrt(ciexyz.y / whitepoint.y),
        )

    @staticmethod
    def HunterLABToCIEXYZ(hunterlab: vec3, whitepoint: vec3) -> vec3:
        var_Ka = 175.0 / 198.04 * (whitepoint.y + whitepoint.x)
        var_Kb = 70.0 / 218.11 * (whitepoint.y + whitepoint.z)
        
        Y = pow(hunterlab.x / whitepoint.y, 2) * 100.0
        X = (hunterlab.y / var_Ka * sqrt(Y / whitepoint.y) + Y / whitepoint.y) * whitepoint.x
        Z = -(hunterlab.z / var_Kb * sqrt(Y / whitepoint.y) - Y / whitepoint.y) * whitepoint.z

        return vec3(X, Y, Z)
    
    # RGB to HSL (hue, saturation, lightness/luminance).
    # Based on: https://gist.github.com/yiwenl/745bfea7f04c456e0101
    @staticmethod
    def RGBToHSL(rgb: vec3) -> vec3:
        cMin: float = min(
            min(
                rgb.r,
                rgb.g,
            ),
            rgb.b,
        )
        cMax: float = max(
            max(
                rgb.r,
                rgb.g,
            ),
            rgb.b,
        )
        delta: float = cMax - cMin
        hsl: vec3 = vec3(0.0, 0.0, (cMax + cMin) / 2.)
        if delta != 0.0:
            if hsl.z < 0.5:
                hsl.y = delta / (cMax + cMin)
            else:
                hsl.y = delta / (2.0 - cMax - cMin)
            deltaR: float = (cMax - rgb.r) / 6.0 / delta + 0.5
            deltaG: float = (cMax - rgb.g) / 6.0 / delta + 0.5
            deltaB: float = (cMax - rgb.b) / 6.0 / delta + 0.5
            if rgb.r == cMax:
                hsl.x = deltaB - deltaG
            elif rgb.g == cMax:
                hsl.x = 1.0 / 3.0 + deltaR - deltaB
            else:
                hsl.x = 2.0 / 3.0 + deltaG - deltaR
            hsl.x = fract(hsl.x)
        return hsl


    @staticmethod
    def HSLToRGB(hsl: vec3) -> vec3:
        if hsl.y == 0.0:
            return vec3(hsl.z)
        b: float
        if hsl.z < 0.5:
            b = hsl.z * (1.0 + hsl.y)
        else:
            b = hsl.z + hsl.y - hsl.y * hsl.z
        a: float = 2.0 * hsl.z - b
        hue: float = fract(hsl.x)
        rgb: float = clamp(
            vec3(
                abs(hue * 6.0 - 3.0) - 1.0,
                2.0 - abs(hue * 6.0 - 2.0),
                2.0 - abs(hue * 6.0 - 4.0)
            ),
            0.0,
            1.0
        )
        return a + rgb * (b - a)

    # RGB to YCbCr, ranges [0, 1].
    # Based on: https://github.com/tobspr/GLSL-Color-Spaces/blob/master/ColorSpaces.inc.glsl
    @staticmethod
    def RGBToYCbCr(rgb: vec3) -> vec3:
        y: float = dot(vec3(0.299, 0.587, 0.114), rgb)
        return vec3(
            y,
            (rgb.b - y) * 0.565,
            (rgb.r - y) * 0.713,
        )

    # YCbCr to RGB.
    @staticmethod
    def YCbCrToRGB(yuv: vec3) -> vec3:
        return vec3(
            yuv.x + 1.403 * yuv.z,
            yuv.x - 0.344 * yuv.y - 0.714 * yuv.z,
            yuv.x + 1.770 * yuv.y
        )

    # XYZ to CIE 1931 Yxy color space (luma (Y) along with x and y chromaticity), I found that Photoshop used this.
    @staticmethod
    def CIEXYZToCIE1931Yxy(xyz: vec3) -> vec3:
        s: float = xyz.x + xyz.y + xyz.z
        return vec3(
            xyz.y,
            xyz.x / s,
            xyz.y / s,
        )

    @staticmethod
    def CIE1931YxyToCIEXYZ(yxy: vec3) -> vec3:
        x: float = yxy.x * (yxy.y / yxy.z)
        return vec3(
            x,
            yxy.x,
            x / yxy.y - x - yxy.x,
        )
    
    # HSV (hue, saturation, value) to RGB.
    # Sources: https://gist.github.com/yiwenl/745bfea7f04c456e0101, https://gist.github.com/sugi-cho/6a01cae436acddd72bdf
    # Changed saturate to clamp, ported to Python.
    @staticmethod
    def HSVToRGB(hsv: vec3) -> vec3:
        K: vec4 = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0)
        return hsv.z * mix(
            K.xxx,
            clamp(
                abs(fract(hsv.x + K.xyz) * 6.0 - K.w) - K.x,
                0.0,
                1.0,
            ),
            hsv.y,
        )

    # RGB to HSV.
    # Source: https://gist.github.com/yiwenl/745bfea7f04c456e0101
    # Ported to Python.
    @staticmethod
    def RGBToHSV(rgb: vec3) -> vec3:
        cMax: float = max(
            max(
                rgb.r,
                rgb.g,
            ),
            rgb.b,
        )
        cMin: float = min(
            min(
                rgb.r,
                rgb.g,
            ),
            rgb.b,
        )
        delta: float = cMax - cMin
        hsv: vec3 = vec3(0.0, 0.0, cMax)
        if cMax > cMin:
            hsv.y = delta / cMax
            if rgb.r == cMax:
                hsv.x = (rgb.g - rgb.b) / delta
            elif rgb.g == cMax:
                hsv.x = 2.0 + (rgb.b - rgb.r) / delta
            else:
                hsv.x = 4.0 + (rgb.r - rgb.g) / delta
            hsv.x = fract(hsv.x / 6.0)
        return hsv

    # Adapted from: https://www.easyrgb.com/en/math.php
    @staticmethod
    def CIEXYZToCIELuv(xyz: vec3, illuminant: vec3) -> vec3:
        var_U = 4.0 * xyz.x / (xyz.x + 15.0 * xyz.y + 3.0 * xyz.z)
        var_V = 9.0 * xyz.y / (xyz.x + 15.0 * xyz.y + 3.0 * xyz.z)

        var_Y = xyz.y / 100.0
        if var_Y > 0.008856:
            var_Y = pow(var_Y, 1.0 / 3.0)
        else:
            var_Y = 7.787 * var_Y + 16.0 / 116.0

        ref_U = 4.0 * illuminant.x / (illuminant.x + 15.0 * illuminant.y + 3.0 * illuminant.z)
        ref_V = 9.0 * illuminant.y / (illuminant.x + 15.0 * illuminant.y + 3.0 * illuminant.z)

        s = 116.0 * var_Y - 16.0
        return vec3(
            s,
            13.0 * s * (var_U - ref_U),
            13.0 * s * (var_V - ref_V),
        )
    
    @staticmethod
    def CIELuvToCIEXYZ(luv: vec3, illuminant: vec3) -> vec3:
        var_Y = (luv.x + 16.0) / 116.0
        if pow(var_Y, 3.0) > 0.008856:
            var_Y = pow(var_Y, 3.0)
        else:
            var_Y = (var_Y - 16.0 / 116.0) / 7.787

        ref_U = 4.0 * illuminant.x / (illuminant.x + 15.0 * illuminant.y + 3.0 * illuminant.z)
        ref_V = 9.0 * illuminant.y / (illuminant.x + 15.0 * illuminant.y + 3.0 * illuminant.z)

        var_U = luv.y / 13.0 / luv.x + ref_U
        var_V = luv.z / 13.0 / luv.x + ref_V

        Y = var_Y * 100
        X =  - ( 9 * Y * var_U ) / ( ( var_U - 4 ) * var_V - var_U * var_V )
        Z = ( 9 * Y - ( 15 * var_V * Y ) - ( var_V * X ) ) / ( 3 * var_V )
        return vec3(X, Y, Z)

    @staticmethod
    def CIEXYZToAdobeRGB(xyz: vec3) -> vec3:
        var_X = xyz.x / 100.0
        var_Y = xyz.y / 100.0
        var_Z = xyz.z / 100.0

        var_R = var_X *  2.04137 + var_Y * -0.56495 + var_Z * -0.34469
        var_G = var_X * -0.96927 + var_Y *  1.87601 + var_Z *  0.04156
        var_B = var_X *  0.01345 + var_Y * -0.11839 + var_Z *  1.01541

        var_R = pow(var_R, 1.0 / 2.19921875)
        var_G = pow(var_G, 1.0 / 2.19921875)
        var_B = pow(var_B, 1.0 / 2.19921875)

        aR = var_R * 255
        aG = var_G * 255
        aB = var_B * 255

        return vec3(aR, aG, aB)

    @staticmethod
    def AdobeRGBToCIEXYZ(argb: vec3) -> vec3:
        var_R = argb.x / 255.0
        var_G = argb.y / 255.0
        var_B = argb.z / 255.0

        var_R = pow(var_R, 2.19921875)
        var_G = pow(var_G, 2.19921875)
        var_B = pow(var_B, 2.19921875)

        var_R = var_R * 100.0
        var_G = var_G * 100.0
        var_B = var_B * 100.0

        X = var_R * 0.57667 + var_G * 0.18555 + var_B * 0.18819
        Y = var_R * 0.29738 + var_G * 0.62735 + var_B * 0.07527
        Z = var_R * 0.02703 + var_G * 0.07069 + var_B * 0.99110

        return vec3(X, Y, Z)
    
    @staticmethod
    def CIEXYZToACESAP1(ciexyz: vec3) -> vec3:
        return ColorSpace.MACESAPM * ciexyz
    
    @staticmethod
    def ACESAP1ToCIEXYZ(ap1: vec3) -> vec3:
        return ColorSpace.MACESAPMInv * ap1

    Edges: dict[tuple[ColorSpaceType, ColorSpaceType], tuple[Callable[[vec3, list[float]], vec3], ColorSpaceParameterType]] = {
        (ColorSpaceType.SRGB, ColorSpaceType.RGB): (SRGBToRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.RGB, ColorSpaceType.SRGB): (RGBToSRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.RGB, ColorSpaceType.CIEXYZ): (RGBToCIEXYZ, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.RGB): (CIEXYZToRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.CIELAB): (CIEXYZToCIELAB, ColorSpaceParameterType.Illuminant | ColorSpaceParameterType.Observer),
        (ColorSpaceType.CIELAB, ColorSpaceType.CIEXYZ): (CIELABToCIEXYZ, ColorSpaceParameterType.Illuminant | ColorSpaceParameterType.Observer),
        (ColorSpaceType.CIELAB, ColorSpaceType.CIELCH): (CartesianToPolar, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIELCH, ColorSpaceType.CIELAB): (PolarToCartesian, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.OKLAB): (CIEXYZToOKLAB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.OKLAB, ColorSpaceType.CIEXYZ): (OKLABToCIEXYZ, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.OKLAB, ColorSpaceType.OKLCH): (CartesianToPolar, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.OKLCH, ColorSpaceType.OKLAB): (PolarToCartesian, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.HunterLAB): (CIEXYZToHunterLAB, ColorSpaceParameterType.Illuminant | ColorSpaceParameterType.Observer),
        (ColorSpaceType.HunterLAB, ColorSpaceType.CIEXYZ): (HunterLABToCIEXYZ, ColorSpaceParameterType.Illuminant | ColorSpaceParameterType.Observer),
        (ColorSpaceType.HunterLAB, ColorSpaceType.HunterLCH): (CartesianToPolar, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.HunterLCH, ColorSpaceType.HunterLAB): (PolarToCartesian, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.RGB, ColorSpaceType.HSL): (RGBToHSL, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.HSL, ColorSpaceType.RGB): (HSLToRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.CIE1931Yxy): (CIEXYZToCIE1931Yxy, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIE1931Yxy, ColorSpaceType.CIEXYZ): (CIE1931YxyToCIEXYZ, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.RGB, ColorSpaceType.YCbCr): (RGBToYCbCr, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.YCbCr, ColorSpaceType.RGB): (YCbCrToRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.RGB, ColorSpaceType.HSV): (RGBToHSV, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.HSV, ColorSpaceType.RGB): (HSVToRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.CIELuv): (CIEXYZToCIELuv, ColorSpaceParameterType.Illuminant | ColorSpaceParameterType.Observer),
        (ColorSpaceType.CIELuv, ColorSpaceType.CIEXYZ): (CIELuvToCIEXYZ, ColorSpaceParameterType.Illuminant | ColorSpaceParameterType.Observer),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.AdobeRGB): (CIEXYZToAdobeRGB, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.AdobeRGB, ColorSpaceType.CIEXYZ): (AdobeRGBToCIEXYZ, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.CIEXYZ, ColorSpaceType.ACESAP1): (CIEXYZToACESAP1, ColorSpaceParameterType.NoParameters),
        (ColorSpaceType.ACESAP1, ColorSpaceType.CIEXYZ): (ACESAP1ToCIEXYZ, ColorSpaceParameterType.NoParameters),
    }

    Graph: DiGraph = DiGraph(Edges.keys())

    @staticmethod
    def convert(
        color: vec3,
        fromColorSpace: ColorSpaceType,
        toColorSpace: ColorSpaceType,
        **kwargs,
    ) -> vec3:
        print(f"Finding shortest path from {fromColorSpace.name} to {toColorSpace.name} with dijkstra.") 
        path = shortest_path(ColorSpace.Graph, fromColorSpace, toColorSpace)
        result: vec3 = color
        for nodeIndex in range(len(path) - 1):
            edge = path[nodeIndex], path[nodeIndex + 1]
            transform, parameterTypes = ColorSpace.Edges[edge]
            parameters = []
            if ColorSpaceParameterType.Illuminant in parameterTypes and \
                ColorSpaceParameterType.Observer in parameterTypes:
                parameters.append(ColorSpace.Tristimuli[kwargs['observer']][kwargs['illuminant']])
            # print("Applying", transform)
            result = transform(result, *parameters)
        return result
    
    @staticmethod
    def SortByCIEH(colors: list[vec3], colorSpace: ColorSpaceType = ColorSpaceType.RGB):
        first = sorted(colors, key=lambda color: length(color))[0]
        # first = colors[0]
        # colors = colors[1:]
        converted = list(map(
            lambda color: ColorSpace.convert(
                color,
                colorSpace,
                ColorSpaceType.CIELCH,
                observer=Observer.TwoDegreesCIE1931,
                illuminant=Illuminant.D65,
            ),
            colors,
        ))
        indices = sorted(
            range(len(colors)),
            key=lambda index: converted[index].z,
        )
        result = list(map(
            lambda index: colors[index],
            indices,
        ))
        while result[0] != first:
            result = result[1:] + [result[0]]
        return result

if __name__ == '__main__':
    from matplotlib import pyplot
    labeldict = {}
    for colorSpaceType in ColorSpaceType:
        labeldict[colorSpaceType] = colorSpaceType.name
    draw(ColorSpace.Graph, with_labels=True, labels=labeldict)
    pyplot.draw()
    pyplot.show()

    result = ColorSpace.convert(
        vec3(.3, .5, .8),
        ColorSpaceType.SRGB,
        ColorSpaceType.CIEXYZ,
        # observer=Observer.TenDegreesCIE1964,
        # illuminant=Illuminant.D75,
    )
    print("result:", result)
    original = ColorSpace.convert(
        result,
        ColorSpaceType.CIEXYZ,
        ColorSpaceType.RGB,
        # observer=Observer.TenDegreesCIE1964,
        # illuminant=Illuminant.D75,
    )
    print("original:", original)
