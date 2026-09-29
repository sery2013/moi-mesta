#!/usr/bin/env python3
import struct, zlib, math, os

def write_png(filename, width, height, pixels):
    """pixels — список (r,g,b,a) для каждого пикселя row by row"""
    def pack_chunk(tag, data):
        c = zlib.crc32(tag + data) & 0xffffffff
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', c)
    
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            r,g,b,a = pixels[y*width+x]
            raw += bytes([r,g,b,a])
    
    compressed = zlib.compress(raw, 9)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = pack_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = pack_chunk(b'IDAT', compressed)
    iend = pack_chunk(b'IEND', b'')
    
    with open(filename, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

def make_icon(size):
    pixels = []
    cx, cy = size/2, size/2
    r = size/2
    
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Круглая форма с anti-aliasing
            alpha = max(0, min(255, int((r - dist + 1.5) * 255)))
            
            if dist < r:
                # Градиент фона: тёмно-зелёный
                t = (y / size)
                bg_r = int(20 + t * 10)
                bg_g = int(38 + t * 15)
                bg_b = int(20 + t * 8)
                
                # Рисуем символ компаса/листа в центре
                # Внешнее кольцо
                ring_outer = r * 0.88
                ring_inner = r * 0.72
                
                in_ring = ring_inner < dist < ring_outer
                
                # Стрелка компаса (треугольники)
                angle = math.atan2(dy, dx)
                norm_angle = (math.degrees(angle) + 360) % 360
                
                # Северная стрелка (вверх) — зелёная
                arrow_r = r * 0.55
                in_north = (dist < arrow_r and dy < 0 and 
                           abs(dx) < (arrow_r + dy) * 0.45)
                # Южная стрелка — серая
                in_south = (dist < arrow_r and dy > 0 and 
                           abs(dx) < (arrow_r - dy) * 0.45)
                
                # Центральная точка
                in_center = dist < r * 0.12
                
                if in_center:
                    pr, pg, pb = 255, 255, 255
                elif in_north:
                    pr, pg, pb = 100, 200, 80
                elif in_south:
                    pr, pg, pb = 160, 160, 160
                elif in_ring:
                    pr, pg, pb = 80, 130, 60
                else:
                    pr, pg, pb = bg_r, bg_g, bg_b
                
                pixels.append((pr, pg, pb, alpha))
            else:
                pixels.append((0, 0, 0, 0))
    
    return pixels

os.makedirs('icons', exist_ok=True)
for size in [192, 512]:
    px = make_icon(size)
    write_png(f'icons/icon-{size}.png', size, size, px)
    print(f'icons/icon-{size}.png создан')
