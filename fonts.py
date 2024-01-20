from oslib import load_bitmap
    
def load_font(bitmap_data, width, char_width, char_height, x_padding=0, y_padding=0):
    font = {}
    pos_x = 0
    pos_y = 0
    for i in range(256):
        font[i] = []
        for y in range(char_height):
            line = []
            for x in range(char_width):
                line.append(bitmap_data[(pos_y + y) * width + pos_x + x])
            font[i].append(line)
        pos_x += char_width + x_padding
        if pos_x + char_width > width:
            pos_x = 0
            pos_y += char_height + y_padding

    return font

base = load_font(load_bitmap("fonts/base.bmp", 128, 128), 128, 6, 8, 2, 0)
