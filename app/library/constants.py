from decimal import Decimal
from math import e

SHORT_TERM_DURATION = Decimal(3)
LONG_TERM_DURATION = Decimal(15)

RANDOMIZED_INITIAL_GRID = True

HAS_INFLUX = False

MINIMUM_AREA = Decimal(800)
MAXIMUM_AREA = Decimal(1000)

BLACKLIST = {
    'Outdoor Sports Complex',
    'Cross-country Skiing Facility',
    'Crop Farm',
    'Grazing Ranch',
    'Regenerative Farm',
    'Solar Array',
    'Agrivoltaic Farm',
    'Agritourist Center',
}

PROPAGATION_STYLE_CHOICES = (0, 1, 2, 3)

PENALTY = Decimal(0.5)
ADVANTAGE = Decimal(3)

MAX_COLOR_VALUE = Decimal(255)
INFLUX_EFFECT = Decimal(1.14888)
_0 = Decimal(0)
_1 = Decimal(1)
_2 = Decimal(2)
_3 = Decimal(3)
_5 = Decimal(5)
_7 = Decimal(7)
_e = Decimal(e)
_100 = Decimal(100)
_neg_1 = Decimal(-1)
