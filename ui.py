import fonts
import math

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
    
    def draw(self, buf, x=0, y=0, x2=0, y2=0, size = 1.5):
        line_height = int(8 * size + 8)
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
                draw_text(buf, x + text_x_offset + 4, (y + option_offset) + (i * line_height) + text_y_offset, item, size, fill=255)
            else:
                draw_text(buf, x + text_x_offset, (y + option_offset) + (i * line_height) + text_y_offset, item, size, fill=0)
            

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
font = fonts.base

def draw_pixel(buf, x, y, fill=0):
    if 0 <= x < buf.width and 0 <= y < buf.height:
        if fill:
            buf.buf[int((x + y * buf.width) / 8)] |= (0x80 >> (x % 8))
        else:
            buf.buf[int((x + y * buf.width) / 8)] &= ~(0x80 >> (x % 8))

def draw_rectangle(buf, x1, y1, x2, y2, fill=0):
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    if x2 > buf.width:
        x2 = buf.width
    if y2 > buf.height:
        y2 = buf.height

    start_byte = x1 // 8
    end_byte = (x2 + 7) // 8
    fill_byte = 0xFF if fill else 0x00

    for y in range(y1, y2):
        start_index = start_byte + y * (buf.width // 8)
        end_index = end_byte + y * (buf.width // 8)
        if fill:
            buf.buf[start_index:end_index] = [fill_byte] * (end_index - start_index)
        else:
            for i in range(start_index, end_index):
                buf.buf[i] &= fill_byte

def draw_char(buf, x, y, char, size=1.0, fill=0):
    # Get the bitmap for the character
    bitmap = font.get(ord(char))
    if bitmap is None:
        return  # Character not supported
    for i, row in enumerate(bitmap):
        for j, col in enumerate(row):
            if col == 1:
                for dy in range(round(size)):
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
    text = text.replace('\\xe2\\x80\\x93', '-')
    text = text.replace(' XC3 XA7', 'ç')
    
    text = text.replace('\\xc2', '?')
    text = text.replace('\\xa0', ' ')
    text = text.replace('\\n', "\n")
    return text

def draw_text(buf, x, y, text, size=1, fill=0):
    for i, char in enumerate(text):
        draw_char(buf, x + math.floor(i*6*size), y, char, size, fill)

def draw_page(buf, text, size, fill, subindex, noRender = False, returnLines = False, ignoreControls=False, yoffset = 0, cachedLines = False):
    draw_rectangle(buf, 0, yoffset, buf.width, buf.height, fill=255)
    max_chars_per_line = int(buf.width // (6 * size))

    controls_offset = 12
    if(ignoreControls):
        controls_offset = 0
    max_lines_per_page = int((buf.height - controls_offset - yoffset) // (9 * size)) - 1

    if not cachedLines:
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
    else:
        lines = cachedLines

    total_pages = len(lines) // max_lines_per_page
    if len(lines) % max_lines_per_page > 0:
        total_pages += 1

    if not noRender:
        if subindex < total_pages:
            for i, line in enumerate(lines[subindex * max_lines_per_page:(subindex + 1) * max_lines_per_page]):
                draw_text(buf, 0, round((i * 9 * size) + 2 + yoffset), line, size, fill)

    if(returnLines):
        return total_pages, lines
    else:
        return total_pages
