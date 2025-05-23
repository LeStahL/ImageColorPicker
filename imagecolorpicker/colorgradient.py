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
    Callable,
)
from enum import (
    IntEnum,
    auto,
)
from copy import deepcopy
from functools import partial
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
)
from construct import (
    Float16l,
    Array,
)
from .colorspace import (
    ColorSpace,
    ColorSpaceType,
    Observer,
    Illuminant,
)
from .optimizationmodel import OptimizationModel


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
    Harmonic = auto()
    Gaussian = auto()


class Wraparound(IntEnum):
    Wrap = auto()
    NoWrap = auto()


class FitAlgorithm(IntEnum):
    LM = auto()
    TRF = auto()
    DogBox = auto()
    CMAES = auto()


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
        fitAlgorithm: FitAlgorithm = FitAlgorithm.LM,
        maxFitIterationCount: int = 5000,
        fitAmount: int = 256,
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
        self._fitAlgorithm: FitAlgorithm = fitAlgorithm
        self._maxFitIterationCount: int = maxFitIterationCount
        self._fitAmount: int = fitAmount
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

    def toDict(self: Self) -> dict:
        return {
            'name': self._name,
            'degree': self._degree,
            'colors': list(map(
                lambda color: [color.x, color.y, color.z],
                self._colors,
            )),
            'weight_color_space': self._weightColorSpace.name,
            'mix_color_space': self._mixColorSpace.name,
            'observer': self._observer.name,
            'illuminant': self._illuminant.name,
            'model': self._model.name,
            'wraparound': self._wraparound.name,
            'algorithm': self._fitAlgorithm.name,
            'max_fit_iteration_count': self._maxFitIterationCount,
            'fit_amount': self._fitAmount,
        }
    
    @classmethod
    def fromDict(cls: type[Self], info: dict) -> 'ColorGradient':
        return cls(
            name=info['name'],
            degree=int(info['degree']),
            colors=list(map(
                lambda components: vec3(*components),
                info['colors'],
            )),
            weightColorSpace = ColorSpaceType[info['weight_color_space']],
            mixColorSpace = ColorSpaceType[info['mix_color_space']],
            observer = Observer[info['observer']],
            illuminant = Illuminant[info['illuminant']],
            model = FitModel[info['model']],
            wraparound = Wraparound[info['wraparound']],
            fitAlgorithm = FitAlgorithm[info['algorithm']],
            maxFitIterationCount = int(info['max_fit_iteration_count']),
            fitAmount = int(info['fit_amount']),
        )

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
    ) -> vec3:
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
                
                result: vec3 = mix(c1, c2, localAmount)

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
        c0: vec3,
    ) -> float:
        costFunction: partial = partial(ColorGradient.colorMapDistance, colorMap=self._coefficients, c0=c0)
        return minimize(costFunction, .5, method='Nelder-Mead').x[0]

    @staticmethod
    def colorMapDistance(t: float, colorMap: List[vec3], c0: vec3) -> float:
        red = [color.r for color in colorMap]
        green = [color.g for color in colorMap]
        blue = [color.b for color in colorMap]
        t = fract(t)
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
        sampledColors: List[vec3] = list(map(
            lambda _amount: self.evaluate(_amount),
            t,
        ))

        initialGuess: list[list[float]]
        model: Callable
        if self._model == FitModel.HornerPolynomial:
            model = OptimizationModel.Polynomial
            initialGuess = OptimizationModel.PolynomialInitialGuess(self._degree)
        elif self._model == FitModel.Trigonometric:
            model = OptimizationModel.Trigonometric
            initialGuess = OptimizationModel.TrigonometricInitialGuess()
        elif self._model == FitModel.Harmonic:
            model = OptimizationModel.Harmonic
            initialGuess = OptimizationModel.HarmonicInitialGuess(self._degree)
        elif self._model == FitModel.Gaussian:
            model = OptimizationModel.Gauss
            initialGuess = OptimizationModel.GaussInitialGuess(self._degree)
        # Fit red
        r = array(list(map(
            lambda color: color.x,
            sampledColors,
        )))
        rp, _ = curve_fit(model, t, r, initialGuess[0], method='trf', loss='arctan', maxfev=5000)

        # Fit green
        g = array(list(map(
            lambda color: color.y,
            sampledColors,
        )))
        gp, _ = curve_fit(model, t, g, initialGuess[1], method='trf', loss='arctan', maxfev=5000)

        # Fit red
        b = array(list(map(
            lambda color: color.z,
            sampledColors,
        )))
        bp, _ = curve_fit(model, t, b, initialGuess[2], method='trf', loss='arctan', maxfev=5000)

        result: List[vec3] = []
        for parameterIndex in range(len(bp)):
            result.append(vec3(
                rp[parameterIndex],
                gp[parameterIndex],
                bp[parameterIndex],
            ))
        print(result)
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

    def evaluateFit(self: Self, t: float) -> vec3:
        model: Callable
        if self._model == FitModel.HornerPolynomial:
            model = OptimizationModel.Polynomial
        elif self._model == FitModel.Trigonometric:
            model = OptimizationModel.Trigonometric
        elif self._model == FitModel.Harmonic:
            model = OptimizationModel.Harmonic
        elif self._model == FitModel.Gaussian:
            model = OptimizationModel.Gauss
        
        return vec3(
            model(t, *list(map(
                lambda fitelement: fitelement.x,
                self._coefficients,
            ))),
            model(t, *list(map(
                lambda fitelement: fitelement.y,
                self._coefficients,
            ))),
            model(t, *list(map(
                lambda fitelement: fitelement.z,
                self._coefficients,
            ))),
        )

    def buildCSSGradient(
        self: Self,
        weight: GradientWeight,
        mix: GradientMix,
    ) -> str:
        amounts: List[float] = list(map(float,range(101)))

        newcolors = list(map(
            lambda amount: self.evaluateFit(float(amount) / 100.),
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
        start: float,
        width: float
    ) -> QLinearGradient:
        stopIndices: list[int] = list(range(101))
        newColors = list(map(
            lambda stopIndex: QColor.fromRgbF(
                *self.evaluateFit(
                    # This is the amount here.
                    float(stopIndex) / 100.,
                ),
            ),
            stopIndices,
        ))

        gradient: QLinearGradient = QLinearGradient()
        gradient.setStart(start, 0)
        gradient.setFinalStop(start + width, 0)
        for stopIndex in stopIndices:
            gradient.setColorAt(float(stopIndex) / 100., newColors[stopIndex])
        
        return gradient
    
    def buildSVGGradient(
        self: Self,
        weight: GradientWeight,
        mix: GradientMix,
    ) -> str:
        amounts: List[float] = list(map(float,range(101)))

        newcolors = list(map(
            lambda amount: self.evaluateFit(float(amount) / 100.),
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

DefaultGradient1 = ColorGradient(
    "Default Gradient 1",
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
DefaultGradient2 = ColorGradient(
    "Default Gradient 2",
    7,
    ColorSpaceType.CIELAB,
    ColorSpaceType.CIELAB,
    [
        vec3(0.02, 0.07, 0.16),
        vec3(0.07, 0.31, 0.41),
        vec3(0.38, 0.67, 0.69),
        vec3(0.95, 0.85, 0.76),
        vec3(0.98, 0.94, 0.83),
        vec3(0.99, 0.92, 0.51),
        vec3(0.92, 0.44, 0.40),
        vec3(0.46, 0.25, 0.33),
    ],
)
