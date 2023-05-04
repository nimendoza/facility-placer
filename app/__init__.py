from pyglet.app import run
from pyglet.graphics import Batch
from pyglet.window import Window
from secrets import choice

from constants import (
    WIDTH,
    HEIGHT,
    CAPTION,
    VALUES_PATH,
    VALUES_SHEETNAMES,
    FACILITIES,
    IMAGE_DATA,
    RESOLUTION,
    ATTACK_DIRECTIONS,
    DIRECTIONS_PATH,
    DIRECTIONS_SHEET,
)
from library import PROPAGATION_STYLE_CHOICES
from utils import (
    center,
    initialize,
    parse_xlsx,
    get_directions,
)

import sys

sys.setrecursionlimit(int(1e9))

window = Window(width=WIDTH, height=HEIGHT,)
window.set_caption(caption=CAPTION)
center(window)

paused = True
batch = Batch()
grid, named_maps = initialize(
    facility_variables=parse_xlsx(VALUES_PATH, *VALUES_SHEETNAMES),
    facilities=FACILITIES,
    image_data=IMAGE_DATA,
    resolution=RESOLUTION,
    height=HEIGHT,
    batch=batch,
)

directions = get_directions(DIRECTIONS_PATH, DIRECTIONS_SHEET, len(grid.values[0]), len(grid.values))

@window.event
def on_key_press(symbol, modifier):
    global paused
    paused = not paused

@window.event
def on_draw():
    window.clear()
    if not paused:
        grid.update(
            named_maps=named_maps,
            attack_directions=ATTACK_DIRECTIONS,
            facilities=FACILITIES,
            directions=directions,
            style=choice(PROPAGATION_STYLE_CHOICES)
        )
    batch.draw()

if __name__  == '__main__':
    run()
