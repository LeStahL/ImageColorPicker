from numpy import (
    array,
    trapezoid,
    linspace,
    ones_like,
    asarray,
    concatenate,
    minimum,
    ones,
    zeros,
    cos,
    acos,
    sin,
    pi,
    exp,
    ndarray,
)
from numpy.linalg import solve
from math import comb


def project(samples, t, basis_count, basis):
    # Evaluate basis
    Phi = array([
        basis(i, t, basis_count)
        for i in range(basis_count)
    ])

    # Construct Gram matrix
    G = array([
        [
            trapezoid(Phi[i] * Phi[j], t)
            for j in range(basis_count)
        ]
        for i in range(basis_count)
    ])

    # Right hand side
    rhs = array([
        trapezoid(samples * Phi[i], t)
        for i in range(basis_count)
    ])

    return solve(G, rhs)

def fourierBasis(i: int, t: ndarray, degree: int) -> ndarray:
    if i == 0:
        return ones_like(t)
    k = (i + 1) // 2
    if i % 2:
        return cos(2 * pi * k * t)
    else:
        return sin(2 * pi * k * t)
    
def fourierGLSL(cmap) -> str:
    first = cmap[0]
    slide = "\n      + ".join(
        (
            # cos terms (i odd)
            [
                f"vec3({cmap[i].x:.2f}, {cmap[i].y:.2f}, {cmap[i].z:.2f}) * "
                f"cos({2.0 * pi * ((i + 1)//2):.2f} * t)"
                for i in range(1, len(cmap), 2)
            ]
            +
            # sin terms (i even)
            [
                f"vec3({cmap[i].x:.2f}, {cmap[i].y:.2f}, {cmap[i].z:.2f}) * "
                f"sin({2.0 * pi * ((i + 1)//2):.2f} * t)"
                for i in range(2, len(cmap), 2)
            ]
        )
    )
    return f"""return vec3({first.x:.2f}, {first.y:.2f}, {first.z:.2f})
      + {slide};"""

def monomialBasis(i: int, t, degree: int):
    return t ** i

def monomialGLSL(coeffs) -> str:
    n = len(coeffs)
    body = f"vec3({coeffs[-1].x:.2f}, {coeffs[-1].y:.2f}, {coeffs[-1].z:.2f})"
    for i in range(n - 2, -1, -1):
        c = coeffs[i]
        body = f"({body} * t + vec3({c.x:.2f}, {c.y:.2f}, {c.z:.2f}))" if i != 0 else f"{body} * t + vec3({c.x:.2f}, {c.y:.2f}, {c.z:.2f})"
    return f"return {body};"

def bernsteinBasis(i: int, t: ndarray, degree: int) -> ndarray:
    n = degree - 1
    return comb(n, i) * (t ** i) * ((1.0 - t) ** (n - i))

def bernsteinGLSL(cmap) -> str:
    n = len(cmap) - 1
    slide = "\n      + ".join(
        [
            f"vec3({cmap[i].x:.2f}, {cmap[i].y:.2f}, {cmap[i].z:.2f}) * "
            f"({comb(n, i):.2f} * pow(t, {i}.0) * pow(1.0 - t, {n - i}.0))"
            for i in range(len(cmap))
        ]
    )
    return f"""return {slide};"""

def chebyshevTBasis(i: int, t: float, degree: int) -> ndarray:
    x = 2.0 * t - 1.0
    return cos(i * acos(x))

def chebyshevTGLSL(cmap) -> str:
    slide = "\n        + ".join(
        [
            f"vec3({cmap[i].x:.2f}, {cmap[i].y:.2f}, {cmap[i].z:.2f}) * "
            f"cos({i:.2f} * acos(t))"
            for i in range(1, len(cmap))
        ]
    )
    first = cmap[0]
    return f"""t = 2.0 * t - 1.0;
    return vec3({first.x:.2f}, {first.y:.2f}, {first.z:.2f})
        + {slide};
"""

def chebyshevUBasis(i: int, t: ndarray, degree: int) -> ndarray:
    x = 2.0 * t - 1.0
    if i == 0:
        return ones_like(x)
    if i == 1:
        return 2.0 * x
    u0 = ones_like(x)
    u1 = 2.0 * x
    for _ in range(2, i + 1):
        u0, u1 = u1, 2.0 * x * u1 - u0
    return u1

def gaussianBasis(i: int, t: ndarray, degree: int):
    center = i / degree
    d = minimum(
        abs(t - center),
        1.0 - abs(t - center)
    )
    sigma = 1.0 / degree
    return exp(-(d**2) / (2.0 * sigma**2))

def gaussianGLSL(cmap) -> str:
    n = len(cmap)
    terms = [
        f"""vec3({cmap[i].x:.2f}, {cmap[i].y:.2f}, {cmap[i].z:.2f}) *
        (exp(-(pow(min(abs(t - float({i}) / float({n})),
                    1.0 - abs(t - float({i}) / float({n}))), 2.0)
        / (2.0 * pow(1.0 / float({n}), 2.0)))) )"""
        for i in range(n)
    ]
    slide = "\n      + ".join(terms)
    return f"""
return {slide};
"""

def rickerBasis(i: int, t: ndarray, degree: int):
    center = i / degree
    d = minimum(
        abs(t - center),
        1.0 - abs(t - center)
    )
    sigma = 1.0 / degree
    x = d / sigma
    return (1.0 - x**2) * exp(-0.5 * x**2)

def bSplineBasis(i: int, t, degree: int):
    t = asarray(t)
    n = degree + 1
    # uniform clamped knot vector
    knots = linspace(0.0, 1.0, n - degree + 1)
    knots = concatenate((
        zeros(degree),
        knots,
        ones(degree)
    ))
    # 0-th order basis
    def N(i, p):
        if p == 0:
            left = knots[i]
            right = knots[i + 1]
            return ((t >= left) & (t < right)).astype(float)
        denom1 = knots[i + p] - knots[i]
        denom2 = knots[i + p + 1] - knots[i + 1]
        term1 = 0.0
        term2 = 0.0
        if denom1 > 0:
            term1 = (t - knots[i]) / denom1 * N(i, p - 1)
        if denom2 > 0:
            term2 = (knots[i + p + 1] - t) / denom2 * N(i + 1, p - 1)
        return term1 + term2
    return N(i, degree)
