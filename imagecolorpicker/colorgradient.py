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
)
from copy import deepcopy
from lmfit.models import PolynomialModel
from imagecolorpicker.color import (
    Color,
    ColorSpace,
)
from functools import partial
from PyQt6.QtGui import QColor

class GradientWeight(IntEnum):
    Oklab = 0x2
    Cielab = 0x3
    RGB = 0x1
    Unweighted = 0x0

class GradientMix(IntEnum):
    Oklab = 0x1
    Cielab = 0x2
    RGB = 0x0

class ColorGradient:
    Degree = 6

    def __init__(
        self: Self,
        *args: Tuple[Color],
    ) -> None:
        self._colors: List[Color] = deepcopy([*args])

    def determineWeights(
        self: Self,
        weight: GradientWeight = GradientWeight.Oklab,
    ) -> List[float]:
        if weight == GradientWeight.Unweighted:
            return list(map(float, linspace(0., 1., len(self._colors) + 1)))[:-1]
        else:
            weights: List[float] = [0.0] * len(self._colors)
            colorspaceDistances: List[float] = [0.0] * len(self._colors)
            totalColorspaceDistance: float = 0.0

            for colorIndex in range(len(self._colors)):
                c1: Color = deepcopy(self._colors[colorIndex])
                c2: Color = deepcopy(self._colors[(colorIndex + 1) % len(self._colors)])

                if weight == GradientWeight.RGB:
                    c1.toColorSpace(ColorSpace.RGB)
                    c2.toColorSpace(ColorSpace.RGB)
                elif weight == GradientWeight.Oklab:
                    c1.toColorSpace(ColorSpace.OKLAB)
                    c2.toColorSpace(ColorSpace.OKLAB)
                elif weight == GradientWeight.Cielab:
                    c1.toColorSpace(ColorSpace.CIELAB)
                    c2.toColorSpace(ColorSpace.CIELAB)

                colorspaceDistance = Color.distance(c1, c2)
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
        weight: GradientWeight = GradientWeight.Oklab,
        mix: GradientMix = GradientMix.Oklab,
        weights: Optional[List[float]] = None,
    ) -> Color:
        amount = fract(amount)
        weights = self.determineWeights(weight) if weights is None else weights

        for colorIndex in range(len(self._colors)):
            if amount < weights[(colorIndex + 1) % len(self._colors)]:
                c1: Color = deepcopy(self._colors[colorIndex % len(self._colors)])
                c2: Color = deepcopy(self._colors[(colorIndex + 1) % len(self._colors)])

                if mix == GradientMix.RGB:
                    c1.toColorSpace(ColorSpace.RGB)
                    c2.toColorSpace(ColorSpace.RGB)
                elif mix == GradientMix.Oklab:
                    c1.toColorSpace(ColorSpace.OKLAB)
                    c2.toColorSpace(ColorSpace.OKLAB)
                elif mix == GradientMix.Cielab:
                    c1.toColorSpace(ColorSpace.CIELAB)
                    c2.toColorSpace(ColorSpace.CIELAB)

                lowerWeight: float = weights[colorIndex]
                upperWeight: float = weights[(colorIndex + 1) % len(self._colors)]
                localAmount: float = (amount - lowerWeight) / abs(upperWeight - lowerWeight)
                
                result: Color = Color.mix(c1, c2, localAmount)
                result.toColorSpace(ColorSpace.RGB)
                return result
        
        c1: Color = deepcopy(self._colors[-1])
        c2: Color = deepcopy(self._colors[0])

        if mix == GradientMix.RGB:
            c1.toColorSpace(ColorSpace.RGB)
            c2.toColorSpace(ColorSpace.RGB)
        elif mix == GradientMix.Oklab:
            c1.toColorSpace(ColorSpace.OKLAB)
            c2.toColorSpace(ColorSpace.OKLAB)
        elif mix == GradientMix.Cielab:
            c1.toColorSpace(ColorSpace.CIELAB)
            c2.toColorSpace(ColorSpace.CIELAB)

        lowerWeight: float = weights[-1]
        localAmount: float = (amount - lowerWeight) / abs(1. - lowerWeight)
        
        result = Color.mix(c1, c2, localAmount)
        result.toColorSpace(ColorSpace.RGB)

        return result
    
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
        weight: GradientWeight = GradientWeight.Oklab,
        mix: GradientMix = GradientMix.Oklab,
    ) -> List[vec3]:
        t = linspace(0., 1., amount)
        sampledColors: List[Color] = list(map(
            lambda _amount: self.evaluate(_amount, weight, mix),
            t,
        ))

        model = PolynomialModel(degree=ColorGradient.Degree)
        
        # Fit red
        r = array(list(map(
            lambda color: color._color.x,
            sampledColors,
        )))
        initialGuess = model.guess(r, t)
        rp, _ = curve_fit(ColorGradient.polynomial, t, r, initialGuess, method='trf', loss='arctan')

        # Fit green
        g = array(list(map(
            lambda color: color._color.y,
            sampledColors,
        )))
        initialGuess = model.guess(g, t)
        gp, _ = curve_fit(ColorGradient.polynomial, t, g, initialGuess, method='trf', loss='arctan')

        # Fit red
        b = array(list(map(
            lambda color: color._color.z,
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
    Color(0.15, 0.18, 0.26),
    Color(0.51, 0.56, 0.66),
    Color(0.78, 0.67, 0.68),
    Color(0.96, 0.75, 0.60),
    Color(0.97, 0.81, 0.55),
    Color(0.97, 0.61, 0.42),
    Color(0.91, 0.42, 0.34),
    Color(0.58, 0.23, 0.22),
)
