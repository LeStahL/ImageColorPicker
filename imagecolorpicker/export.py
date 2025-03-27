from .representation import Representation
from .language import Language
from glm import vec3
from .colorgradient import ColorGradient, DefaultGradient1, DefaultGradient2, FitModel
from typing import (
    Callable,
    Union,
    ByteString,
    Optional,
)
from re import sub
from construct import (
    Float16l,
    Array,
    Subconstruct,
    Struct,
)
from glm import ceil, sqrt
from functools import reduce
from PyQt6.QtGui import QColor


class Export:
    @staticmethod
    def NearestSquareRoot(number: int) -> int:
        return int(ceil(sqrt(float(number))))

    @staticmethod
    def MakeIdentifier(name: str) -> str:
        return sub('\W|^(?=\d)', '_', name)

    @staticmethod
    def Export(
        language: Language,
        representation: Representation,
        selectedGradient: ColorGradient,
        gradientList: list[ColorGradient],
        selectedColor: vec3,
    ) -> Optional[Union[ByteString, str]]:
        if language == Language.GLSL:
            if representation == Representation.ColorMap:
                cmap: list[vec3] = selectedGradient.coefficients
                if selectedGradient._model == FitModel.HornerPolynomial:
                    openStack: str = '\n        +t*('.join(map(
                        lambda color: f'vec3({color.x:.2f}, {color.y:.2f}, {color.z:.2f})',
                        cmap,
                    ))
                    closeStack: str = ')' * (len(cmap) - 1)
                    return f'vec3 cmap_{Export.MakeIdentifier(selectedGradient._name)}(float t) {{\n    return {openStack}\n    {closeStack};\n}}\n'
                elif selectedGradient._model == FitModel.Trigonometric:
                    return f'vec3 cmap_{Export.MakeIdentifier(selectedGradient._name)}(float t) {{\n    return vec3({cmap[0].x:.4f}, {cmap[0].y:.4f}, {cmap[0].z:.4f}) + vec3({cmap[1].x:.4f}, {cmap[1].y:.4f}, {cmap[1].z:.4f}) * cos(2. * pi * (vec3({cmap[2].x:.4f}, {cmap[2].y:.4f}, {cmap[2].z:.4f}) * t + vec3({cmap[3].x:.4f}, {cmap[3].y:.4f}, {cmap[3].z:.4f})));\n}}\n'
            elif representation == Representation.Color3:
                return f'vec3({selectedColor.x:.2f}, {selectedColor.y:.2f}, {selectedColor.z:.2f})'
            elif representation == Representation.Color4:
                return f'vec4({selectedColor.x:.2f}, {selectedColor.y:.2f}, {selectedColor.z:.2f}, 1)'
            elif representation == Representation.NearestWeight:
                return f'{selectedGradient.nearestWeightInColorMap(selectedColor):.2f}'
            elif representation == Representation.Colors:
                colorSlide = ',\n    '.join(list(map(
                    lambda color: f'vec3({color.x:.2f}, {color.y:.2f}, {color.z:.2f})',
                    selectedGradient._colors,
                )))
                name: str = Export.MakeIdentifier(selectedGradient._name)
                return f'const int {name}_color_count = {selectedGradient.colorCount};\nconst vec3 {name}_colors[] = vec3[](\n    {colorSlide}\n);\n'
            elif representation == Representation.Weights:
                weightSlide = ',\n    '.join(list(map(
                    lambda weight: f'{weight:.2f}',
                    selectedGradient._weights,
                )))
                name: str = Export.MakeIdentifier(selectedGradient._name)
                return f'const int {name}_weight_count = {len(selectedGradient._weights)};\nconst float {name}_weights[] = float[](\n    {weightSlide}\n);\n'
            elif representation == Representation.ColorMaps:
                cmaps: list[list[vec3]] = reduce(
                    lambda accumulator, addition: accumulator + addition,
                    map(
                        lambda gradient: gradient.coefficients,
                        gradientList,
                    ),
                )
                coefficientSlide = ',\n    '.join(list(map(
                    lambda color: f'vec3({color.x:.2f}, {color.y:.2f}, {color.z:.2f})',
                    cmaps,
                )))
                cmap_offsets = []
                offset = 0
                for gradient in gradientList:
                    cmap_offsets.append(offset)
                    offset += len(gradient.coefficients)
                cmap_offsets.append(len(cmaps))
                offsetSlide = ',\n    '.join(map(
                    str,
                    cmap_offsets,
                ))
                return f'const int all_cmap_coefficient_count = {len(cmaps)};\nconst int offsets_per_cmap[] = int[](\n    {offsetSlide}\n);\nconst vec3 all_cmap_coefficients[] = vec3[](\n    {coefficientSlide}\n);\nvec3 cmap(int index, float t) {{\n    vec3 a = all_cmap_coefficients[offsets_per_cmap[index + 1] - 1];\n    for(int i = offsets_per_cmap[index + 1] - 2; i >= offsets_per_cmap[index]; --i) {{\n        a = all_cmap_coefficients[i] + t * a;\n    }}\n    return a;\n}}'
        elif language == Language.HLSL:
            pass
        elif language == Language.CSS:
            if representation == Representation.ColorMap:
                colorStops = list(map(
                    lambda amount: selectedGradient.evaluateFit(float(amount) / 100.),
                    list(map(float, range(101))),
                ))
                colorSlide: str = ', '.join(map(
                    lambda colorStop: f'{QColor.fromRgbF(*colorStop).name()}',
                    colorStops,
                ))
                return f'linear-gradient({colorSlide})'
        elif language == Language.SVG:
            if representation == Representation.ColorMap:
                amounts = list(map(float, range(101)))
                colorStops = list(map(
                    lambda amount: selectedGradient.evaluateFit(float(amount) / 100.),
                    amounts,
                ))
                colorSlide: str = '\n  '.join(map(
                    lambda stopIndex: f'<stop stop-color="{QColor.fromRgbF(*colorStops[stopIndex]).name()}" offset="{int(amounts[stopIndex])}%" />',
                    range(len(amounts)),
                ))
                return f'<linearGradient>\n{colorSlide}\n</linearGradient>'
        elif language == Language.Python:
            pass
        elif language == Language.NASM:
            pass
        elif language == Language.C:
            pass


if __name__ == '__main__':
    print(Export.Export(
        Language.SVG,
        Representation.ColorMap,
        DefaultGradient1,
        [DefaultGradient1, DefaultGradient2],
        # vec3(.3,.6,.8),
        vec3(0),
    ))
