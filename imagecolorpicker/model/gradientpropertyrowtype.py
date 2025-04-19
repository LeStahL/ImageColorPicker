from enum import (
    IntEnum,
    auto,
)


class GradientPropertyRowType(IntEnum):
    Name = auto()
    Degree = auto()
    WeightColorSpace = auto()
    MixColorSpace = auto()
    Observer = auto()
    Illuminant = auto()
    Model = auto()
    Wraparound = auto()
    FitAlgorithm = auto()
    MaxFitIterationCount = auto()
    FitAmount = auto()
