from enum import IntEnum, auto


class Representation(IntEnum):
    ColorMap = auto()
    Picked3ComponentColor = auto()
    Picked4ComponentColor = auto()
    PickedNearestGradientWeight = auto()
    GradientColorArray = auto()
    GradientWeightArray = auto()
