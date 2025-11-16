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
    sin,
    sqrt,
    exp,
    log,
)
from lmfit.models import PolynomialModel


class OptimizationModel:
    @staticmethod
    def TrigonometricInitialGuess() -> list[list[float]]:
        return [
            [1.] * 4,
            [1.] * 4,
            [1.] * 4,
        ]

    @staticmethod
    def Trigonometric(t: float, *p: tuple[float]) -> float:
        a, b, c, d = p
        return a + b * cos(2. * pi * (c * t + d))

    @staticmethod
    def PolynomialInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * (degree - 2),
            [1.] * (degree - 2),
            [1.] * (degree - 2),
        ]

    @staticmethod
    def Polynomial(t: float, *c: tuple[float]) -> float:
        o = len(c) + 1
        result = c[-1]
        for ck in reversed(c[:-1]):
            result = ck + t * result
        # Make periodic
        result += 1. / (o - 2) * (c[o - 2] - sum(map(lambda i: i * c[i] - c[i - 1], range(2, o - 1)))) * t ** (o - 1)
        result += ((1 - o) / (o - 2) * (c[o - 2] - sum(map(lambda i: i * c[i] - c[i - 1], range(2, o - 1)))) - sum(map(lambda i: i * c[i], range(2, o - 1)))) * t ** o
        return result

    @staticmethod
    def FourierInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]

    @staticmethod
    def Fourier(t: float, *c: tuple[float]) -> float:
        result = c[0]
        for k in range(1, len(c)):
            result += c[k] * cos(pi * k * t)
        return result

    @staticmethod
    def ExponentialInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]

    @staticmethod
    def Exponential(t: float, *c: tuple[float]) -> float:
        result = 0.0
        for k in range(len(c)):
            result +=  c[k] * exp(-k * t)
        return result
