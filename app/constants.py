'''
For formula constants, kindly refer to app.library.constants
'''
from library import Facility

WIDTH = 1000
HEIGHT = 822

RESOLUTION = 20  # Must be in multiples of 10

CAPTION = 'IMMC 2023 Prototype'

INPUT_DIRECTORY = 'input'
IMAGE_DIRECTORY = 'img'

DIRECTIONS_PATH = f'{INPUT_DIRECTORY}/directions.xlsx'
DIRECTIONS_SHEET = 'main'

IMAGE_NAMES = (
    'topography',
    'cell_coverage',
    'tree_cover',
    'distance_from_road',
    'distance_from_water',
)

IMAGE_DATA = tuple(
    (
        f'{IMAGE_DIRECTORY}/{name}.png',
        0,
        name
    ) for name in IMAGE_NAMES
)

VALUES_PATH = f'{INPUT_DIRECTORY}/values_.xlsx'
VALUES_SHEETNAMES = (
    'B_s',
    'B_l',
    'C_s',
    'C_l',
)

FACILITIES = (
    Facility(
        name='Outdoor Sports Complex',
        color=(0, 255, 242),
    ),
    Facility(
        name='Cross-country Skiing Facility',
        color=(198, 0, 229),
    ),
    Facility(
        name='Crop Farm',
        color=(216, 0, 57),
    ),
    Facility(
        name='Grazing Ranch',
        color=(198, 150, 29),
    ),
    Facility(
        name='Regenerative Farm',
        color=(8, 180, 22),
    ),
    Facility(
        name='Solar Array',
        color=(18, 110, 29),
    ),
    Facility(
        name='Agrivoltaic Farm',
        color=(198, 190, 229),
    ),
    Facility(
        name='Agritourist Center',
        color=(189, 170, 249),
    ),
)

ATTACK_DIRECTIONS = {
    'N': (0, 1),
    'NE': (1, 1),
    'E': (1, 0),
    'SE': (1, -1),
    'S': (0, -1),
    'SW': (-1, -1),
    'W': (-1, 0),
    'NW': (-1, 1),
}
