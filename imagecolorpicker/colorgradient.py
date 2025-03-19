from __future__ import annotations
from scipy.optimize import curve_fit, minimize
from numpy import (
    array,
    array,
    linspace,
)
from glm import (
    vec3,
    fract,
    length,
    mix,
)
from typing import (
    Self,
    Tuple,
    List,
    Optional,
)
from enum import (
    IntEnum,
    IntFlag,
    auto,
)
from copy import deepcopy
from lmfit.models import PolynomialModel
from imagecolorpicker.color import (
    Color,
    ColorSpaceType,
)
from functools import partial
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
)
from construct import (
    Float16l,
    Float16b,
    Array,
)
from .colorspace import (
    ColorSpace,
    ColorSpaceType,
    Observer,
    Illuminant,
)


class GradientWeight(IntEnum):
    Oklab = 0x2
    Cielab = 0x3
    RGB = 0x1
    Unweighted = 0x0

class GradientMix(IntEnum):
    Oklab = 0x1
    Cielab = 0x2
    RGB = 0x0

class FitModel(IntEnum):
    Trigonometric = auto()
    HornerPolynomial = auto()

class Wraparound(IntEnum):
    Wrap = auto()
    NoWrap = auto()

class ColorGradient:
    def __init__(
        self: Self,
        name: str,
        degree: int,
        weightColorSpace: ColorSpaceType,
        mixColorSpace: ColorSpaceType,
        colors: list[vec3],
        observer: Observer = Observer.TwoDegreesCIE1931,
        illuminant: Illuminant = Illuminant.D65,
        model: FitModel = FitModel.HornerPolynomial,
        wraparound: Wraparound = Wraparound.Wrap,
    ) -> None:
        self._name: str = name
        self._degree: int = degree
        self._colors: list[vec3] = deepcopy(colors)
        self._weightColorSpace: ColorSpaceType = weightColorSpace
        self._mixColorSpace: ColorSpaceType = mixColorSpace
        self._observer: Observer = observer
        self._illuminant: Illuminant = illuminant
        self._model: FitModel = model
        self._wraparound: Wraparound = wraparound
        self._weights: list[float] = [0.] * self.colorCount
        self._coefficients: list[vec3] = [vec3(0)] * self.colorCount
        self._update()

    @property
    def colorCount(self: Self) -> int:
        return len(self._colors)

    @property
    def weights(self: Self) -> list[float]:
        return self._weights

    @property
    def coefficients(self: Self) -> list[vec3]:
        return self._coefficients

    def _update(self: Self) -> None:
        self._weights = self.determineWeights()
        self._coefficients = self.fit()

    def toDict(self: Self) -> None:
        return {}

    def determineWeights(
        self: Self,
    ) -> List[float]:
        weights: List[float] = [0.0] * len(self._colors)
        colorspaceDistances: List[float] = [0.0] * len(self._colors)
        totalColorspaceDistance: float = 0.0
        colorCount: int = self.colorCount if self._wraparound == Wraparound.Wrap else (self._colorCount - 1)
        for colorIndex in range(colorCount):
            c1 = ColorSpace.convert(
                self._colors[colorIndex],
                ColorSpaceType.SRGB,
                self._weightColorSpace,
                observer=self._observer,
                illuminant=self._illuminant,
            )
            c2 = ColorSpace.convert(
                self._colors[(colorIndex + 1) % len(self._colors)],
                ColorSpaceType.SRGB,
                self._weightColorSpace,
                observer=self._observer,
                illuminant=self._illuminant,
            )

            colorspaceDistance = length(c1 - c2)
            colorspaceDistances[colorIndex] = colorspaceDistance
            totalColorspaceDistance += colorspaceDistance

        totalDistance: float = 0.0
        for colorIndex in range(len(self._colors)):
            colorspaceDistances[colorIndex] /= totalColorspaceDistance
            weights[colorIndex] = totalDistance
            totalDistance += colorspaceDistances[colorIndex]
        
        return weights

    def evaluate(
        self: Self,
        amount: float,
    ) -> Color:
        amount = fract(amount)
        for colorIndex in range(self.colorCount):
            if amount < self.weights[(colorIndex + 1) % self.colorCount]:
                c1 = ColorSpace.convert(
                    self._colors[colorIndex % self.colorCount],
                    ColorSpaceType.SRGB,
                    self._mixColorSpace,
                    observer=self._observer,
                    illuminant=self._illuminant,
                )
                c2 = ColorSpace.convert(
                    self._colors[(colorIndex + 1) % self.colorCount],
                    ColorSpaceType.SRGB,
                    self._mixColorSpace,
                    observer=self._observer,
                    illuminant=self._illuminant,
                )

                lowerWeight: float = self.weights[colorIndex]
                upperWeight: float = self.weights[(colorIndex + 1) % len(self._colors)]
                localAmount: float = (amount - lowerWeight) / abs(upperWeight - lowerWeight)
                
                result: Color = mix(c1, c2, localAmount)

                return ColorSpace.convert(
                    result,
                    self._mixColorSpace,
                    ColorSpaceType.SRGB,
                    observer=self._observer,
                    illuminant=self._illuminant,
                )
        
        c1 = ColorSpace.convert(
            self._colors[-1],
            ColorSpaceType.SRGB,
            self._mixColorSpace,
            observer=self._observer,
            illuminant=self._illuminant,
        )
        c2 = ColorSpace.convert(
            self._colors[0],
            ColorSpaceType.SRGB,
            self._mixColorSpace,
            observer=self._observer,
            illuminant=self._illuminant,
        )

        lowerWeight: float = self.weights[-1]
        localAmount: float = (amount - lowerWeight) / abs(1. - lowerWeight)
        
        result = mix(c1, c2, localAmount)
        return ColorSpace.convert(
            result,
            self._mixColorSpace,
            ColorSpaceType.SRGB,
            observer=self._observer,
            illuminant=self._illuminant,
        )
    
    def nearestWeightInColorMap(
        self: Self,
        colorMap: List[vec3],
        c0: vec3,
    ) -> float:
        costFunction: partial = partial(ColorGradient.colorMapDistance, colorMap=colorMap, c0=c0)
        return minimize(costFunction, .5, method='Nelder-Mead').x[0]

    @staticmethod
    def colorMapDistance(t: float, colorMap: List[vec3], c0: vec3) -> float:
        red = [color.r for color in colorMap]
        green = [color.g for color in colorMap]
        blue = [color.b for color in colorMap]
        
        return length(vec3(
            ColorGradient.polynomial(t, *red),
            ColorGradient.polynomial(t, *green),
            ColorGradient.polynomial(t, *blue),
        ) - c0)

    def fit(
        self: Self,
        amount: int = 256,
    ) -> List[vec3]:
        t = linspace(0., 1., amount)
        sampledColors: List[Color] = list(map(
            lambda _amount: self.evaluate(_amount),
            t,
        ))
        model = PolynomialModel(degree=self._degree)
        
        # Fit red
        r = array(list(map(
            lambda color: color.x,
            sampledColors,
        )))
        initialGuess = model.guess(r, t)
        rp, _ = curve_fit(ColorGradient.polynomial, t, r, initialGuess, method='trf', loss='arctan')

        # Fit green
        g = array(list(map(
            lambda color: color.y,
            sampledColors,
        )))
        initialGuess = model.guess(g, t)
        gp, _ = curve_fit(ColorGradient.polynomial, t, g, initialGuess, method='trf', loss='arctan')

        # Fit red
        b = array(list(map(
            lambda color: color.z,
            sampledColors,
        )))
        initialGuess = model.guess(b, t)
        bp, _ = curve_fit(ColorGradient.polynomial, t, b, initialGuess, method='trf', loss='arctan')

        result: List[vec3] = []
        for parameterIndex in range(len(bp)):
            result.append(vec3(
                rp[parameterIndex],
                gp[parameterIndex],
                bp[parameterIndex],
            ))
        return result
    
    def allColorMaps(
        self: Self,
    ) -> List[Tuple[GradientWeight, GradientMix, List[vec3]]]:
        result = []
        for weight in GradientWeight:
            for mix in GradientMix:
                result.append((weight, mix, self.fit(weight=weight, mix=mix)))
        return result
    
    def buildColorMap(
        self: Self,
        weight: GradientWeight = GradientWeight.Oklab,
        mix: GradientMix = GradientMix.Oklab,
        slug: str = '_example',
    ) -> str:
        result: List[vec3] = self.fit(weight=weight, mix=mix)
        return """vec3 cmap_{weight}{mix}{slug}(float t) {{
    return {open}
    {close};
}}
""".format(
        open='\n        +t*('.join(map(
            lambda resultIndex: 'vec3({:.2f},{:.2f},{:.2f})'.format(*result[resultIndex]),
            range(len(result)),
        )),
        close=')' * (len(result) - 1),
        mix=mix.name,
        weight=weight.name,
        slug=slug,
    )

    def buildPythonBinary(
        self: Self,
        weight: GradientWeight = GradientWeight.Oklab,
        mix: GradientMix = GradientMix.Oklab,
        slug: str = '_example',
    ) -> str:
        result: List[vec3] = self.fit(weight=weight, mix=mix)
        print(result)
        zwischenresult = b''.join(map(
            lambda resultIndex: b''.join(list(map(
                lambda resultComponent: Float16l.build(resultComponent),
                result[resultIndex],
            ))),
            range(len(result)),
        ))
        print(len(zwischenresult), zwischenresult)
        print(Array(21, Float16l).parse(zwischenresult))
        moreresult = f"# Color map coefficients for {slug}\n" + str(zwischenresult)
        return moreresult
    
    def buildNasmBinary(
        self: Self,
        weight: GradientWeight = GradientWeight.Oklab,
        mix: GradientMix = GradientMix.Oklab,
        slug: str = '_example',
    ) -> str:
        result: List[vec3] = self.fit(weight=weight, mix=mix)
        return f"; Color map coefficients for {slug}\n" + str(b''.join(map(
            lambda resultIndex: b''.join(reversed(list(map(
                lambda resultComponent: Float16l.build(resultComponent),
                result[resultIndex],
            )))),
            range(len(result)),
        ))) + ","

    @staticmethod
    def evaluateFit(t: float, fit: List[vec3]) -> vec3:
        result: vec3 = vec3(0)
        for parameterIndex in range(len(fit)):
            parameter: vec3 = fit[parameterIndex]
            result += parameter * pow(t, float(parameterIndex))
        return result

    def buildCSSGradient(
        self: Self,
        weight: GradientWeight,
        mix: GradientMix,
    ) -> str:
        fitresult: List[vec3] = self.fit(256, weight, mix)
        amounts: List[float] = list(map(float,range(101)))

        newcolors = list(map(
            lambda amount: ColorGradient.evaluateFit(float(amount) / 100., fitresult),
            amounts,
        ))

        return """linear-gradient({colors});""".format(
            colors=', '.join(map(
                lambda resultIndex: '{color}'.format(
                    color=QColor.fromRgbF(*newcolors[resultIndex]).name(),
                ),
                range(len(newcolors)),
            )),
        )

    def linearGradient(
        self: Self,
        width: float
    ) -> QLinearGradient:
        stopIndices: list[int] = list(range(101))
        newColors = list(map(
            lambda stopIndex: QColor.fromRgbF(
                *ColorGradient.evaluateFit(
                    # This is the amount here.
                    float(stopIndex) / 100.,
                    self.coefficients,
                ),
            ),
            stopIndices,
        ))

        gradient: QLinearGradient = QLinearGradient()
        gradient.setStart(0, 0)
        gradient.setFinalStop(width, 0)
        for stopIndex in stopIndices:
            gradient.setColorAt(float(stopIndex) / 100., newColors[stopIndex])
        
        return gradient
    
    def buildSVGGradient(
        self: Self,
        weight: GradientWeight,
        mix: GradientMix,
    ) -> str:
        fitresult: List[vec3] = self.fit(256, weight, mix)
        amounts: List[float] = list(map(float,range(101)))

        newcolors = list(map(
            lambda amount: ColorGradient.evaluateFit(float(amount) / 100., fitresult),
            amounts,
        ))

        return """<linearGradient>
    {colors}
</linearGradient>""".format(
            colors='\n    '.join(map(
                lambda resultIndex: '<stop stop-color="{color}" offset="{offset}%" />'.format(
                    color=QColor.fromRgbF(*newcolors[resultIndex]).name(),
                    offset=int(amounts[resultIndex]),
                ),
                range(len(newcolors)),
            )),
        )

    @staticmethod
    def polynomial(t: float, *c: Tuple[float]) -> float:
        result = c[-1]
        for ck in reversed(c[:-1]):
            result = ck + t * result
        return result

DefaultGradient = ColorGradient(
    "Default Gradient",
    7,
    ColorSpaceType.OKLAB,
    ColorSpaceType.OKLAB,
    [
        vec3(0.15, 0.18, 0.26),
        vec3(0.51, 0.56, 0.66),
        vec3(0.78, 0.67, 0.68),
        vec3(0.96, 0.75, 0.60),
        vec3(0.97, 0.81, 0.55),
        vec3(0.97, 0.61, 0.42),
        vec3(0.91, 0.42, 0.34),
        vec3(0.58, 0.23, 0.22),
    ],
)
