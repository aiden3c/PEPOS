import fonts
import math

class Buffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buf = bytearray(math.ceil(width * height / 8))

class Menu:
    def __init__(self, options):
        self.selection = 0
        self.options = options

    def select_next(self):
        self.selection = (self.selection + 1) % len(self.options)
        return self.selection

    def select_previous(self):
        self.selection = (self.selection - 1) % len(self.options)
        return self.selection

    def get_selected_option(self):
        return self.options[self.selection]
    
    def draw(self, buf, x=0, y=0, x2=0, y2=0):
        width = buf.width
        height = buf.height
        line_height = 20
        text_y_offset = line_height / 4
        text_x_offset = 4
        y += (-line_height * self.selection)

        float_x_offset = 0
        if(x > 0 or y > 0 or x2 < buf.width or y2 < buf.height):
            float_x_offset = 2

        draw_rectangle(buf, x, y, x2, y2, fill=255)

        #determine how many option lines can show up in the box made from x,y,x2,y2
        options_on_screen = int((y2 - y) / line_height)

        for i, item in enumerate(self.options):
            if i >= options_on_screen:
                break
            #option offset, if self.selection * negative line height is greater than the height of the menu, then we need to offset the y value
            option_offset = self.selection * line_height
            if(option_offset < y):
                break
            if(i == self.selection):
                draw_rectangle(buf, x + float_x_offset, (y + option_offset) + (i * line_height), x2 - float_x_offset, (y + option_offset) + (i * line_height) + line_height, fill=0)
                draw_text(buf, x + text_x_offset + 4, (y + option_offset) + (i * line_height) + text_y_offset, item, 1.5, fill=255)
            else:
                draw_text(buf, x + text_x_offset, (y + option_offset) + (i * line_height) + text_y_offset, item, 1.5, fill=0)
            

def draw_line(buf, x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        # Set the pixel at the current position
        if 0 <= x1 < buf.width and 0 <= y1 < buf.height:
            buf.buf[int((x1 + y1 * buf.width) / 8)] &= ~(0x80 >> (x1 % 8))

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# Define the font as a dictionary of bitmaps
font = fonts.basic

def draw_pixel(buf, x, y, fill=0):
    if 0 <= x < buf.width and 0 <= y < buf.height:
        if fill:
            buf.buf[int((x + y * buf.width) / 8)] |= (0x80 >> (x % 8))
        else:
            buf.buf[int((x + y * buf.width) / 8)] &= ~(0x80 >> (x % 8))

def draw_rectangle(buf, x1, y1, x2, y2, fill=0):
    for x in range(x1, x2):
        for y in range(y1, y2):
            draw_pixel(buf, x, y, fill)

def draw_char(buf, x, y, char, size=1, fill=0):
    # Get the bitmap for the character
    bitmap = font.get(char.upper())
    if bitmap is None:
        return  # Character not supported

    # Draw the character
    for i, row in enumerate(bitmap):
        for j, col in enumerate(bin(row)[2:].zfill(5)):
            if col == '1':
                for dy in range(math.ceil(size)):
                    for dx in range(math.ceil(size)):
                        draw_pixel(buf, x + math.floor(j*size) + dx, y + math.floor(i*size) + dy, fill)

def text_bounds(text, size=1):
    char_width = 6
    char_height = 8

    text_width = len(text) * char_width * size
    text_height = char_height * size

    return text_width, text_height

def fix_unicode(text):
    text = text.replace('\\xe2\\x80\\x99', "'")
    text = text.replace('\\xe2\\x80\\x98', '"')
    text = text.replace('\\xe2\\x80\\x9c', '"')
    text = text.replace('\\xe2\\x80\\x9d', '"')
    text = text.replace('\\xe2\\x80\\x94', '-')
    text = text.replace('\\xc2', '?')
    text = text.replace('\\xa0', ' ')
    text = text.replace('\\n', "")
    return text

def draw_text(buf, x, y, text, size=1, fill=0):
    for i, char in enumerate(text):
        draw_char(buf, x + math.floor(i*6*size), y, char, size, fill)

def draw_page(buf, text, size, fill, subindex, noRender = False, yoffset = 0):
    print("Drawing page")
    draw_rectangle(buf, 0, yoffset, buf.width, buf.height, fill=255)
    max_chars_per_line = int(buf.width // (6 * size))
    max_lines_per_page = int((buf.height - 12 - yoffset) // (8 * size)) - 1

    lines = []

    for paragraph in text.split('\n'):
        if not paragraph:
            lines.append('')
            continue

        words = paragraph.split(' ')
        current_line = ''

        for word in words:
            if len(current_line) + len(word) + 1 > max_chars_per_line:
                lines.append(current_line.strip())
                current_line = ''

            current_line += word + ' '

        lines.append(current_line.strip())

    total_pages = len(lines) // max_lines_per_page
    if len(lines) % max_lines_per_page > 0:
        total_pages += 1

    if(noRender):
        return total_pages

    if subindex < total_pages:
        for i, line in enumerate(lines[subindex * max_lines_per_page:(subindex + 1) * max_lines_per_page]):
            print(line)
            draw_text(buf, 0, round((i * 8 * size) + 2 + yoffset), line, size, fill)

    return total_pages