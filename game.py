from typing import List, Union, Set
from random import shuffle

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str((self.x, self.y))
    __repr__ = __str__

    def __add__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate(self.x + other.x,
                          self.y + other.y)

    def __eq__(self, other: "Coordinate"):
        return (self.x, self.y) == (other.x, other.y)
    def __ne__(self, other: "Coordinate"):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        return (self.x, self.y)

    def is_valid(self):
        return 0 <= self.x < Board.SIZES[0] and 0 <= self.y < Board.SIZES[1]


class Cell:
    EMPTY, RED, BLUE, BOMB = -4, -3, -2, -1
    BOMBS = (RED, BLUE, BOMB)
    EMOJI_UNICODE_SWITCH = {f":keycap_{x}:": x for x in range(1, 9)} | {
        " ": 0,
        ":white_large_square:": EMPTY,
        ":blue_circle:": BLUE,
        ":red_circle:": RED,
        ":bomb:": BOMB}

    NEIGHBORS = [Coordinate(i, j) for i in range(-1, 2) for j in range(-1, 2) if i or j]

    def __init__(self, value: int, coordinate: Coordinate):
        self.is_mine = self.is_empty = self.is_value = False
        self.mine_possibility = None
        self.value = self.color = None
        self.coordinate = coordinate

        if value == Cell.EMPTY:
            self.is_empty = True
        elif value in Cell.BOMBS:
            self.is_mine = True
            self.color = value
        else:
            self.is_value = True
            self.value = value

    def __str__(self):
        return " " if self.is_empty \
            else str(self.value) if self.is_value \
            else {Cell.RED: "R", Cell.BLUE: "B", Cell.BOMB: "*"}[self.color]
    __repr__ = __str__

    def __lt__(self, other: "Cell"):
        if self.mine_possibility is None:
            return False
        if other.mine_possibility is None:
            return True
        return self.mine_possibility < other.mine_possibility
    def __eq__(self, other: "Cell"):
        if (self.mine_possibility is None) ^ (other.mine_possibility is None):
            return False
        return self.mine_possibility == other.mine_possibility


class Board:
    SIZES = (8, 7)
    NO_MINES = 15

    def __init__(self, raw_board: List[List[int]]):
        self.board = [[Cell(cell, Coordinate(ri, ci)) for ci, cell in enumerate(row)] for ri, row in enumerate(raw_board)]

    def __str__(self):
        return "\n".join(map(lambda row: f"|{'|'.join(map(str, row))}|", self.board))
    __repr__ = __str__

    def __getitem__(self, coordinate: Coordinate) -> Cell:
        return self.board[coordinate.x][coordinate.y]

    def choose(self) -> Cell:
        self.define_zones()

        result_cell = self.set_possibilities()
        if result_cell is None:
            shuffle(self.empty_cells)
            self.empty_cells.sort()
            result_cell = self.empty_cells.pop()

        return result_cell

    def define_zones(self) -> None:
        self.zones : List[Zone] = []
        for ri, row in enumerate(self.board):
            for ci, cell in enumerate(row):
                if cell.is_value:
                    self.zones.append(Zone(self, Coordinate(ri, ci)))

        for _ in range(3):
            no_zones = len(self.zones)
            for zi in range(no_zones):
                for zj in range(zi+1, no_zones):
                    zone_i = self.zones[zi]
                    zone_j = self.zones[zj]
                    if zone_i & zone_j and zone_i.value != zone_j.value:
                        new_zone = zone_i - zone_j if zone_i.value > zone_j.value else zone_j - zone_i
                        if new_zone.value != 0 and new_zone not in self.zones:
                            self.zones.append(new_zone)

    def set_possibilities(self) -> Union[Cell, None]:
        self.empty_cells = []
        mine_cells = []
        for row in self.board:
            for cell in row:
                if cell.is_empty:
                    self.empty_cells.append(cell)
                elif cell.is_mine:
                    mine_cells.append(cell)

        for zi, zone_i in enumerate(self.zones):
            if zone_i.value == 0:
                for coordinate in zone_i:
                    for zj, zone_j in enumerate(self.zones):
                        if zi != zj:
                            zone_j.remove(coordinate)
                    cell = self[coordinate]
                    cell.mine_possibility = 0
                    if cell in self.empty_cells:
                        self.empty_cells.remove(cell)

                del self.zones[zi]

            elif len(zone_i) == zone_i.value:
                for coordinate in zone_i:
                    self[coordinate].mine_possibility = 1
                return self[zone_i.pop()]

        for zone in self.zones:
            if len(zone) != 0:
                zone_possibility = zone.value / len(zone)
                for coordinate in zone:
                    cell = self[coordinate]
                    if cell.mine_possibility is None:
                        cell.mine_possibility = zone_possibility
                    else:
                        cell.mine_possibility = min(zone_possibility, cell.mine_possibility)

        total_possibility = (Board.NO_MINES - len(mine_cells)) / len(self.empty_cells)
        for cell in self.empty_cells:
            if cell.mine_possibility is not None and cell.mine_possibility != 0:
                cell.mine_possibility = total_possibility

        return None


class Zone:
    def __init__(self, board: Board = None, home_coordinate: Coordinate = None,
                       coordinates: Set[Coordinate] = None, value: int = None):
        if board:
            self.value = board[home_coordinate].value
            self.coordinates = set()

            for neighbor_plus_coordinate in Cell.NEIGHBORS:
                neighbor_coordinate = home_coordinate + neighbor_plus_coordinate
                if neighbor_coordinate.is_valid():
                    neighbor = board[neighbor_coordinate]
                    if neighbor.is_mine:
                        self.value -= 1
                    elif neighbor.is_empty:
                        self.coordinates.add(neighbor_coordinate)

        else:
            self.value = value
            self.coordinates = coordinates

    def __str__(self):
        return str(self.coordinates)
    __repr__ = __str__

    def __contains__(self, item: Coordinate) -> bool:
        return item in self.coordinates

    def __sub__(self, other: "Zone") -> "Zone":
        return Zone(coordinates=self.coordinates - other.coordinates,
                    value=self.value - other.value)

    def __and__(self, other: "Zone") -> Set[Coordinate]:
        return self.coordinates.intersection(other)

    def __iter__(self):
        return iter(self.coordinates)

    def __len__(self) -> int:
        return len(self.coordinates)

    def remove(self, item: Coordinate) -> None:
        self.coordinates.discard(item)

    def pop(self) -> Coordinate:
        return self.coordinates.pop()
