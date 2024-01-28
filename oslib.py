from typing import Callable

class Command:
    def __init__(self, name: str, *arguments):
        self.name = name
        self.arguments = arguments

class Application:
    def __init__(self, name: str, init: Callable, run: Callable, kill: Callable, variables: dict, menuOptions={}):
        self.name = name
        self.init = init
        self.run = run
        self.kill = kill
        self.variables = variables
        self.menuOptions = menuOptions

class OSSetting:
    def __init__(self, name: str, value):
        self.name = name
        self.value = value

class BufferUpdate:
    def __init__(self, x: int, y: int, x2: int, y2: int):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2

class Buffer:
    def __init__(self, width: int, height: int, data: int = 0xFF):
        self.width = width
        self.height = height
        self.buf = [data] * (int(width/8) * height)
        self.update = BufferUpdate(width, height, 0, 0) #Inverted buffer update, means first draw will actually make proper buf
    
    def resetUpdate(self):
        self.update = BufferUpdate(self.width, self.height, 0, 0)

class Buffer2Bit:
    def __init__(self, width: int, height: int, data = 0xFF):
        self.width = width
        self.height = height
        self.buf = [data] * (int(width/4) * height)

#This assumes you are updating within (0,0) to (buf.width, buf.height). Could cause damage otherwise!
def buffer_update_merge(buf: Buffer, update: BufferUpdate):
    source = buf.update
    #Create the rectangle that encapsulates the entire updated area
    source.x = min(source.x, update.x)
    source.y = min(source.y, update.y)
    source.x2 = max(source.x2, update.x2)
    source.y2 = max(source.y2, update.y2)

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
transparent = 0xBF
