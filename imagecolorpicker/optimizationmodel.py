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
from math import comb
from numpy import where


class OptimizationModel:
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
        result = c[0] * cos(pi * 2 * c[1])
        for k in range(1, len(c) // 2):
            result += c[2 * k] * cos(pi * 2 * (k * t + c[2 * k + 1]))
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

    @staticmethod
    def ChebyshevTInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]
    
    @staticmethod
    def ChebyshevT(t: float, *c: tuple[float]) -> float:
        result = 0.0
        tnm1 = 1.0
        tn = t
        for k in range(len(c)):
            result += c[k] * tnm1
            tnp1 = 2 * t * tn - tnm1
            tnm1 = tn
            tn = tnp1
        return result

    @staticmethod
    def ChebyshevUInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]
    
    @staticmethod
    def ChebyshevU(t: float, *c: tuple[float]) -> float:
        result = 0.0
        tnm1 = 1.0
        tn = 2 * t
        for k in range(len(c)):
            result += c[k] * tnm1
            tnp1 = 2 * t * tn - tnm1
            tnm1 = tn
            tn = tnp1
        return result

    @staticmethod
    def GaussianInitialGuess(degree: int) -> list[list[float]]:
        result = []
        for _ in range(3):
            coeffs = []
            for k in range(degree // 3):
                coeffs.extend([
                    1.0,
                    (k + 0.5) / degree,
                    0.25,
                ])
            result.append(coeffs)
        return result

    @staticmethod
    def Gaussian(t: float, *c: tuple[float]) -> float:
        result = 0.0
        for k in range(len(c) // 3):
            amplitude = c[3 * k]
            center = c[3 * k + 1]
            sigma = abs(c[3 * k + 2]) + 1e-6
            x = (t - center) / sigma
            result += amplitude * exp(-x * x)
        return result

    @staticmethod
    def BernsteinInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]


    @staticmethod
    def Bernstein(t: float, *c: tuple[float]) -> float:
        n = len(c) - 1
        result = 0.0
        for i in range(len(c)):
            result += (
                c[i]
                * comb(n, i)
                * t**i
                * (1.0 - t)**(n - i)
            )
        return result

    @staticmethod
    def HaarInitialGuess(degree: int) -> list[list[float]]:
        return [
            [1.] * degree,
            [1.] * degree,
            [1.] * degree,
        ]
    
    @staticmethod
    def HaarBasis(t: float, level: int, shift: int):
        scale = 1 << level
        x = t * scale - shift
        return where(
            (x >= 0.0) & (x < 1.0),
            where(
                x < 0.5,
                1.0,
                -1.0,
            ),
            0.0,
        )

    @staticmethod
    def Haar(t: float, *c: tuple[float]) -> float:
        result = c[0]
        index = 1
        level = 0
        while index < len(c):
            count = 1 << level
            for shift in range(count):
                if index >= len(c):
                    break
                result += c[index] * OptimizationModel.HaarBasis(t, level, shift)
                index += 1
            level += 1
        return result
