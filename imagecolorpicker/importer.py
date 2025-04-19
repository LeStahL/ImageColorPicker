from glm import vec3


class Importer:
    @staticmethod
    def HornerPolynomial(source: str) -> list[vec3]:
        stacks = list(map(
            lambda stack: stack.rstrip().lstrip(),
            source.replace('return ', '').rstrip(';} \t\n').split('+t*('),
        ))
        stacks[-1], _ = stacks[-1].split()
        return list(map(
            lambda stack: eval(stack),
            stacks,
        ))
