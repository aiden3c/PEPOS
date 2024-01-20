class Command:
    def __init__(self, name, *arguments):
        self.name = name
        self.arguments = arguments

class Application:
    def __init__(self, name, init, run, kill, variables, menuOptions={}):
        self.name = name
        self.init = init
        self.run = run
        self.kill = kill
        self.variables = variables
        self.menuOptions = menuOptions

class Buffer:
    def __init__(self, width, height, data = 0xFF):
        self.width = width
        self.height = height
        self.buf = [data] * (int(width/8) * height)

class Buffer2Bit:
    def __init__(self, width, height, data = 0xFF):
        self.width = width
        self.height = height
        self.buf = [data] * (int(width/4) * height)

def nop(*_):
    return True

def load_bitmap(path, width, height, inv = False, raw = False):
    ret = []
    with open(path, 'rb') as file:
        file.seek(10)
        data_offset = int.from_bytes(file.read(4), 'little')
        file.seek(data_offset)

        bitmap_data = file.read()
        for y in range(height):
            line = []
            for x in range(width):
                pos = y * width + x
                pixel = bitmap_data[pos // 8] & (0b10000000 >> (pos % 8))
                line.append(pixel)
            ret.extend(line[::-1])
        ret = ret[::-1]
        if raw:
            return ret
        realret = []
        for i in range(len(ret)):
            if inv:
                realret.append(0 if ret[i] else 1)
            else:
                realret.append(1 if ret[i] else 0)
        return realret

white = 0xFF
gray1 = 0xC0
gray2 = 0x80
black = 0x00

