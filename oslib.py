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

def nop(*_):
    return True