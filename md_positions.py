# -*- coding: utf-8 -*-
CENTER_X = 149
HOUSEX = 80
HOUSEY = 169
FOOT8 = 130

# md_place -> (f_stone_y, pp_x_offset)
# md_place: 5=3b, 4=3f, 3=2b, 2=2f, 1=1b, 0=1f
_PLACE = {
    5: (360, 72),
    4: (380, 72),
    3: (420, 70),
    2: (440, 70),
    1: (480, 68),
    0: (500, 68),
}


def get_md_stones(md_place: int, is_ppl: bool, is_ppr: bool,
                  f: int, l: int) -> list[tuple]:
    f_y, x_off = _PLACE[md_place]
    if is_ppl:
        return [(CENTER_X - HOUSEX, HOUSEY, l), (CENTER_X - x_off, f_y, f)]
    elif is_ppr:
        return [(CENTER_X + HOUSEX, HOUSEY, l), (CENTER_X + x_off, f_y, f)]
    else:
        return [(CENTER_X, FOOT8, l), (CENTER_X, f_y, f)]
