
class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    def tuple(self):
        return (self.r, self.g, self.b)

    @classmethod
    def fromInt(self, i):
        mask = 0xFF
        return Color(
            (i >> 16) & mask,
            (i >> 8) & mask,
            (i >> 0) & mask
        )

    def __str__(self):
        return "(%d, %d, %d)" % (self.r, self.g, self.b)


class LedMatrix:
    def __init__(self, width, height):
        self.data = [Color(0, 0, 0)] * (width * height)
        self.width = width
        self.height = height

    def get(self, row, col):
        return self.data[self.width * row + col]

    def set(self, row, col, color):
        self.data[self.width * row + col] = color

    def clear(self, color = Color(0, 0, 0)):
        self.data = [color] * (self.width * self.height)

class LedMapping:
    def __init__(self):
        self.data = {}

    def set(self, row, col, index):
        self.data[(row, col)] = index

    def get(self, row, col):
        return self.data[(row, col)]


def mapMatrixToBytes(ledMatrix: LedMatrix, ledMapping: LedMapping):
    bytes = [0] * ledMatrix.width * ledMatrix.height * 4

    for r in range(0, ledMatrix.height):
        for c in range(0, ledMatrix.width):
            idx = ledMapping.get(r, c)
            color = ledMatrix.get(r, c)

            bytes[idx * 4 + 0] = color.r
            bytes[idx * 4 + 1] = color.g
            bytes[idx * 4 + 2] = color.b
            bytes[idx * 4 + 3] = 0
    
    return bytes
