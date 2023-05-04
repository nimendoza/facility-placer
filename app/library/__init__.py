from collections import defaultdict
from decimal import Decimal
from math import log
from pyglet.graphics import Batch
from pyglet.shapes import Rectangle as PygletRectangle
from secrets import randbelow
from typing import Any, Iterable, Optional

from .constants import (
    SHORT_TERM_DURATION,
    LONG_TERM_DURATION,
    RANDOMIZED_INITIAL_GRID,
    HAS_INFLUX,
    MINIMUM_AREA,
    MAXIMUM_AREA,
    BLACKLIST,
    PENALTY,
    ADVANTAGE,
    MAX_COLOR_VALUE,
    INFLUX_EFFECT,
    _0,
    _1,
    _2,
    _3,
    _5,
    _7,
    _e,
    _100,
    _neg_1,
)

def ln(value: Decimal):
    return Decimal(log(value))

def color_code_to_value(value: Decimal):
    return value * _100 / MAX_COLOR_VALUE

class Facility:
    name: str
    color: tuple[int, int, int]

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.color = kwargs['color']

    def average(
            self,
            map: list[list[Any]],
            connected_cells: Iterable[tuple[int, int]]
    ):
        return sum(
            map[y][x] * _100 / MAX_COLOR_VALUE
            for x, y in connected_cells 
        ) / len(connected_cells)
        
    def short_term_benefits(self):
        return self.short_term_wages * self.short_term_workers
    
    def revenue(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
        has_influx: bool,
    ):
        return (
            (
                _1 + color_code_to_value(named_maps['cell_coverage'][y][x])
            ) * self.average_revenue
            * (INFLUX_EFFECT if has_influx else 1)
        )
    
    def clean_energy_benefits(self):
        return (
            self.solar_reduction
            * (
                _2 / _3 * pow(
                    base=self.percent_solar,
                    exp=(_5 / _2)
                ) - _1 / _3
            )
        )

    def long_term_benefits(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
        has_influx: bool,
    ):
        return self.revenue(
            named_maps=named_maps,
            x=x,
            y=y,
            has_influx=has_influx,
        ) + (
            self.long_term_wages * self.long_term_workers
        ) + self.clean_energy_benefits()
    
    def accessibility_price(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
    ):
        return self.accessibility_factor * color_code_to_value(named_maps['distance_from_road'][y][x])
    
    def irrigation_price(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
    ):
        return self.irrigation_factor * color_code_to_value(named_maps['distance_from_water'][y][x])
    
    def deforestation_price(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
    ):
        return self.deforestation_factor * color_code_to_value(named_maps['tree_cover'][y][x])
    
    def construction_price(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
        connected_cells: Iterable[tuple[int, int]] | None,
    ):
        area = Decimal(len(connected_cells)) if connected_cells is not None else _1
        average_topography = self.average_topography if connected_cells is not None else _1
        return area * self.construction_factor * (
            _1 - abs(
                _1 - self.constant * color_code_to_value(named_maps['topography'][y][x]) / average_topography
            )
        )
    
    def labor_price(self):
        return self.short_term_wages * self.short_term_workers

    def short_term_costs(
        self,
        connected_cells: Iterable[tuple[int, int]] | None,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
    ):
        return (
            self.accessibility_price(
                named_maps=named_maps,
                x=x,
                y=y,
            ) + self.irrigation_price(
                named_maps=named_maps,
                x=x,
                y=y,
            ) + self.deforestation_price(
                named_maps=named_maps,
                x=x,
                y=y,
            ) + self.construction_price(
                named_maps=named_maps,
                x=x,
                y=y,
                connected_cells=connected_cells,
            ) + self.labor_price()
        )
    
    def carbon_taxation(
        self,
        connected_cells: Iterable[tuple[int, int]] | None,
    ):
        area = Decimal(len(connected_cells)) if connected_cells is not None else _1
        return area * self.taxation_factor * max(_0, self.carbon_produced - self.upper_carbon_limit)
    
    def long_term_costs(
        self,
        connected_cells: Iterable[tuple[int, int]] | None,
    ):
        return self.operating_costs + self.utility_costs + self.carbon_taxation(
            connected_cells=connected_cells
        )

    def ldmr_multiplier(
        self,
        connected_cells: Iterable[tuple[int, int]] | None,
    ):
        if connected_cells is None:
            return _1
        area = Decimal(len(connected_cells))
        if area < MINIMUM_AREA:
            return pow(
                base=_e,
                exp=(
                    _neg_1 * _7 / MINIMUM_AREA * area
                    + ln(ADVANTAGE - _1)
                    + _7 / MINIMUM_AREA
                ),
            )
        if area > MAXIMUM_AREA:
            return PENALTY + _1 / (
                area - MAXIMUM_AREA + _5
            )
        return _1
    
    def score(
        self,
        named_maps: dict[str, list[list[int]]],
        x: int,
        y: int,
        connected_cells: Optional[Iterable[tuple[int, int]]] = None,
    ):
        return (
            (
                self.short_term_benefits() * SHORT_TERM_DURATION
                + self.long_term_benefits(
                    named_maps=named_maps,
                    x=x,
                    y=y,
                    has_influx=HAS_INFLUX,
                ) * LONG_TERM_DURATION
            ) / (
                self.short_term_costs(
                    named_maps=named_maps,
                    x=x,
                    y=y,
                    connected_cells=connected_cells,
                ) * SHORT_TERM_DURATION
                + self.long_term_costs(
                    connected_cells=connected_cells
                ) * LONG_TERM_DURATION
            ) * self.ldmr_multiplier(
                connected_cells=connected_cells
            )
        )

class Rectangle(PygletRectangle):
    facility: Facility
    connected_cells: Iterable[tuple[int, int]]

    def __init__(self, **kwargs):
        self.facility = kwargs.pop('facility')
        super().__init__(**kwargs)

def valid(x: int, y: int, grid: list):
    return all([
        0 <= x < len(grid[0]),
        0 <= y < len(grid),
    ]) and grid[y][x]

def neighbors(x: int, y: int, grid: list[list[Any]]):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if valid(x + dx, y + dy, grid):
                yield (x + dx, y + dy)

class Grid:
    values: list[list[Rectangle | None]]

    def __init__(
        self,
        named_maps: dict[str, list[list[int]]],
        merged_map: list[list[dict[str, int]]],
        facilities: Iterable[Facility],
        resolution: int,
        batch: Batch,
        height: int,
    ):
        self.values = [[None for _ in row] for row in merged_map]
        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if any(merged_map[y][x].values()):
                    best_facility = None
                    best_score = -1
                    for facility in facilities:
                        if facility.name in BLACKLIST:
                            continue
                        score = randbelow(100) if RANDOMIZED_INITIAL_GRID else facility.score(
                            named_maps=named_maps,
                            x=x,
                            y=y,
                        )
                        if score > best_score:
                            best_facility = facility
                            best_score = score
                    self.values[y][x] = Rectangle(
                        x=x * resolution,
                        y=height - y * resolution,
                        width=resolution,
                        height=resolution,
                        color=best_facility.color,
                        batch=batch,
                        facility=best_facility,
                    )
    
    def clear_connected_cell_data(self):
        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if self.values[y][x]:
                    self.values[y][x].connected_cells = None

    def set_connected_cell_data(
        self,
        named_maps: dict[str, list[list[int]]],
    ):
        def bfs_(
            connected_component: set,
            x: int,
            y: int,
        ):
            connected_component.add((x, y))
            for dx, dy in (
                (1, 0),
                (0, 1),
                (-1, 0),
                (0, -1)
            ):
                u = x + dx
                v = y + dy
                if valid(u, v, self.values):
                    if all([
                        (u, v) not in connected_component,
                        self.values[v][u].facility == self.values[y][x].facility,
                    ]):
                        bfs_(connected_component, u, v)

        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if self.values[y][x]:
                    if getattr(self.values[y][x], 'connected_cells', None) is None:
                        connected_component = set()
                        bfs_(connected_component, x, y)
                        connected_component = tuple(connected_component)
                        average_topography = self.values[y][x].facility.average(
                            map=named_maps['topography'],
                            connected_cells=connected_component
                        )
                        for u, v in connected_component:
                            setattr(self.values[v][u], 'connected_cells', connected_component)
                            setattr(self.values[v][u].facility, 'average_topography', average_topography)

    def get_preferred_direction(
        self,
        facilities: Iterable[Facility],
        directions: dict[str, set],
    ):
        seen = set()
        record = dict((facility, defaultdict(int)) for facility in facilities)
        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if self.values[y][x] and (x, y) not in seen:
                    seen.update(self.values[y][x].connected_cells)
                    for u, v in self.values[y][x].connected_cells:
                        for direction, group in directions.items():
                            if (u, v) in group:
                                record[self.values[v][u].facility][direction] += 1
                                break
        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if self.values[y][x]:
                    self.values[y][x].preferred_direction = max(
                        record[self.values[y][x].facility],
                        key=lambda direction: record[self.values[y][x].facility][direction]
                    )

    def update(
        self,
        named_maps: dict[str, list[list[int]]],
        attack_directions: dict[str, tuple[int, int]],
        facilities: Iterable[Facility],
        directions: dict[str, set],
        style: int,
    ):
        self.clear_connected_cell_data()
        self.set_connected_cell_data(named_maps)
        self.get_preferred_direction(
            facilities=facilities,
            directions=directions,
        )

        total_score = _0
        region_count = _0
        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if self.values[y][x]:
                    region_count += _1
                    total_score += self.values[y][x].facility.score(
                        named_maps=named_maps,
                        x=x,
                        y=y,
                        connected_cells=self.values[y][x].connected_cells,
                    )
        print(total_score / region_count)

        for y in range(len(self.values)):
            for x in range(len(self.values[y])):
                if self.values[y][x]:
                    surrounded_by_tally = defaultdict(Decimal)
                    surrounded_by_scores = defaultdict(Decimal)
                    can_attack = set()
                    for nx, ny in neighbors(x=x, y=y, grid=self.values):
                        if all([
                            self.values[ny][nx].facility != self.values[y][x].facility,
                            (nx - x, ny - y) == attack_directions[self.values[ny][nx].preferred_direction]
                        ]):
                            can_attack.add(self.values[ny][nx].facility)
                        surrounded_by_tally[self.values[ny][nx].facility] += 1
                        surrounded_by_scores[self.values[ny][nx].facility] += self.values[ny][nx].facility.score(
                            named_maps=named_maps,
                            x=nx,
                            y=ny,
                            connected_cells=self.values[ny][nx].connected_cells,
                        )
                    for facility, tally in surrounded_by_tally.items():
                        surrounded_by_scores[facility] /= tally
                    
                    new_value = None
                    can_rank_by_score = surrounded_by_scores and self.values[y][x].facility == min(
                        surrounded_by_scores,
                        key=lambda facility: surrounded_by_scores[facility]
                    )
                    can_rank_by_tally = surrounded_by_tally and self.values[y][x].facility == min(
                        surrounded_by_tally,
                        key=lambda facility: surrounded_by_tally[facility]
                    )
                    match style:
                        case 0:
                            if can_rank_by_score:
                                new_value = sorted(
                                    surrounded_by_scores,
                                    key=lambda facility: surrounded_by_scores[facility]
                                )[-1]
                        case 1:
                            if can_rank_by_score:
                                new_value = sorted(
                                    can_attack.union((None,)),
                                    key=lambda facility: surrounded_by_scores[facility]
                                )[-1]
                        case 2:
                            if can_rank_by_tally:
                                new_value = sorted(
                                    surrounded_by_tally,
                                    key=lambda facility: surrounded_by_tally[facility]
                                )[-1]
                        case 3:
                            if can_rank_by_tally:
                                new_value = sorted(
                                    can_attack.union((None,)),
                                    key=lambda facility: surrounded_by_tally[facility]
                                )[-1]
                    if new_value:
                        self.values[y][x].facility = new_value
                        self.values[y][x].color = new_value.color
