def load_bitmap(path, width, height, inv = False):
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
        realret = []
        for i in range(len(ret)):
            if inv:
                realret.append(0 if ret[i] else 1)
            else:
                realret.append(1 if ret[i] else 0)
        return realret
    
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
