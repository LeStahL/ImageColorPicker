from enum import (
    IntEnum,
    auto,
)
from typing import Self
# from glm import *
from numpy import (
    array,
    array,
    linspace,
    cos,
    pi,
)
from lmfit.models import PolynomialModel


class OptimizationModel:
    @staticmethod
    def CosineInitialGuess() -> list[list[float]]:
        return [
            [1.] * 4,
            [1.] * 4,
            [1.] * 4,
        ]

    @staticmethod
    def Cosine(t: float, *p: tuple[float]) -> float:
        a, b, c, d = p
        return a + b * cos(2. * pi * (c * t + d))

    @staticmethod
    def PolynomialInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]

    @staticmethod
    def Polynomial(t: float, *c: tuple[float]) -> float:
        result = c[-1]
        for ck in reversed(c[:-1]):
            result = ck + t * result
        return result
