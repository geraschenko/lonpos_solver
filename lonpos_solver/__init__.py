"""A Lonpos solver."""

import dataclasses
from typing import Iterator, List, Optional, Tuple, Union
import numpy as np
import matplotlib.pyplot as plt


@dataclasses.dataclass
class Piece:
  """Represents a piece"""
  name: str
  color: str
  definition: List[Tuple[int, int]]


PIECES = (
    Piece('A', 'orange', ((0, 0), (1, 0), (1, 1), (1, 2))),
    Piece('B', 'red', ((0, 0), (0, 1), (1, 0), (1, 1), (1, 2))),
    Piece('C', 'blue', ((0, 0), (1, 0), (1, 1), (1, 2), (1, 3))),
    Piece('D', 'pink', ((0, 0), (1, 0), (1, 1), (1, 2), (1, -1))),
    Piece('E', 'green', ((0, 0), (0, 1), (1, 1), (1, 2), (1, 3))),
    Piece('F', 'whitesmoke', ((0, 0), (1, 0), (1, 1))),
    Piece('G', 'cyan', ((0, 0), (1, 0), (2, 0) ,(2, 1), (2, 2))),
    Piece('H', 'magenta', ((0, 0), (1, 0), (1, 1) ,(2, 1), (2, 2))),
    Piece('I', 'yellow', ((0, 0), (0, 1), (1, 0), (2, 0) ,(2, 1))),
    Piece('J', 'darkviolet', ((0, 0), (0, 1), (0, 2), (0, 3))),
    Piece('K', 'lime', ((0, 0), (0, 1), (1, 0), (1, 1))),
    Piece('L', 'gray', ((0, 0), (1, 0), (1, 1), (1, -1), (2, 0))),
)


def normalized_tuple(coords: np.ndarray) -> Tuple[Tuple[int, ...], ...]:
  """A canonicalized and hashable version of a set of coordinates."""
  return tuple(sorted(tuple(p) for p in coords))


def all_2d_rotations_and_translations(definition: List[Tuple[int, int]]
    ) -> List[np.ndarray]:
  """All possible displacements of a piece which contain (0, 0)."""
  rot90 = np.array([[0, -1], [1, 0]])
  flip = np.array([[-1, 0], [0, 1]])
  xy = []
  coords = np.array(definition)
  for _ in range(2):
    for _ in range(4):
      for offset in coords:
        xy.append(coords - offset)
      coords = coords @ rot90
    coords = coords @ flip
  xy = set(normalized_tuple(p) for p in xy)  # de-dupe
  return [np.array(p) for p in xy]


def rectangle_board() -> np.ndarray:
  return np.zeros((11, 5), dtype='uint8')


def triangle_board() -> np.ndarray:
  board = np.zeros((10, 10), dtype='uint8')
  for i in range(10):
    for j in range(9 - i):
      board[j, i] = -1
  return board


def arrowhead_board() -> np.ndarray:
  board = np.zeros((9, 9), dtype='uint8')
  board[0, [0, 1, 2, 3, 6, 7, 8]] = -1
  board[[0, 1, 2, 3, 6, 7, 8], 0] = -1
  board[1, [1, 2, 3, 7, 8]] = -1
  board[[1, 2, 3, 7, 8], 1] = -1
  board[2, [2, 8]] = -1
  board[[2, 8], 2] = -1
  board[5, 6] = -1
  return board


def butterfly_board() -> np.ndarray:
  board = np.zeros((9, 9), dtype='uint8')
  board[0, [0, 1, 2, 3, 8]] = -1
  board[1, [0, 1, 2, 3]] = -1
  board[2, [0, 1]] = -1
  board[3, [0, 1]] = -1
  board = board + board[::-1, ::-1]
  return board


class Lonpos2D:
  """A Lonpos solver for 2D boards."""

  def __init__(self, board_type: Optional[str] = None):
    self.piece = {i + 1: p for i, p in enumerate(PIECES)}
    self.piece_idx = {p.name: i for i, p in self.piece.items()}
    orientations = {}
    for i, piece in self.piece.items():
      coord_list = all_2d_rotations_and_translations(piece.definition)
      orientations[i] = tuple(np.array(coords) for coords in coord_list)
    self.orientations = orientations

    boards = {'triangle': triangle_board,
              'arrowhead': arrowhead_board,
              'butterfly': butterfly_board,
              }
    self.set_board(boards.get(board_type, rectangle_board)())
    self.board_type = board_type

  def __repr__(self):
    return f'Lonpos2D({self.board_type!r})'


  def set_board(self, board: np.ndarray) -> None:
    """Sets a board position."""
    self.board = board.copy()
    used_indices = np.unique(board)
    self.remaining_pieces = [p.name for i, p in self.piece.items()
                                 if i not in used_indices]

  def completed(self) -> bool:
    """True if the board is completed."""
    return len(self.remaining_pieces) == 0 and (self.board != 0).all()


  def in_bounds(self, x: int, y: int) -> bool:
    return 0 <= x < self.board.shape[0] and 0 <= y < self.board.shape[1]


  def next_pos(self) -> Tuple[int, int]:
    """A good candidate position on the board to try to fill."""
    # Returns an empty spot with 1 neighbor if possible, 2 neighbors otherwise.
    candidate = None
    empty = [(x, y) for x in range(self.board.shape[0])
                 for y in range(self.board.shape[1]) if not self.board[x, y]]
    offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for p in empty:
      nbrs = [(p[0] + i, p[1] + j) for i, j in offsets]
      nbrs = [n for n in nbrs if self.in_bounds(n[0], n[1])]
      num_neighbors = sum(n in empty for n in nbrs)
      if num_neighbors in [0, 1]:
        return p
      if candidate is None and  num_neighbors == 2:
        candidate = p
    return candidate


  def can_place(self, xy: np.ndarray) -> bool:
    return (all(self.in_bounds(x, y) for x, y in xy) and
            not self.board[xy[:, 0], xy[:, 1]].any())


  def _place(self, xy: np.ndarray, index: int) -> None:
    self.board[xy[:, 0], xy[:, 1]] = index


  def place(self, name: str, xy: np.ndarray) -> None:
    """Adds the given piece to the board at the given coordinates."""
    assert name in self.remaining_pieces, f'piece {name} not available'
    index = self.piece_idx[name]
    valid_xy = set(normalized_tuple(xy_) for xy_ in self.orientations[index])
    assert normalized_tuple(xy - xy[0]) in valid_xy, (
        f'Not a valid orientation of piece {name}:\n{xy}')
    assert self.can_place(xy), f'cannot place at {xy}'
    self._place(xy, self.piece_idx[name])
    self.remaining_pieces.remove(name)


  def get_xy(self, name):
    """Returns the coordinates of a piece on the board."""
    index = self.piece_idx[name]
    if not (self.board == index).any():
      raise ValueError(f'{name} is not on the board')
    x, y = (self.board == index).nonzero()
    return np.array(list(zip(x, y)))


  def unplace(self, *names):
    """Removes the given pieces from the board."""
    for name in names:
      xy = self.get_xy(name)
      self._place(xy, 0)
      self.remaining_pieces.append(name)


  def plot(self, board: Optional[np.ndarray] = None, ax=None) -> None:
    """Displays the board."""
    if ax is None:
      ax = plt.gca()
    if board is None:
      board = self.board
    ax.set_facecolor('lightgray')
    ax.set_xlim(-.6, board.shape[0] - .4)
    ax.set_ylim(-.6, board.shape[1] - .4)
    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    for x in range(board.shape[0]):
      for y in range(board.shape[1]):
        idx = board[x, y]
        if idx == 255:
          pass
        elif idx:
          piece = self.piece[idx]
          ax.add_patch(plt.Circle((x, y), 0.5, facecolor=piece.color,
            edgecolor='black', clip_on=False))
          ax.text(x, y, piece.name, ha='center', va='center')
        else:
          ax.add_patch(plt.Circle((x, y), 0.4, color='white', clip_on=False))


  def solutions(self) -> Iterator[np.ndarray]:
    """All solutions from the given position."""
    if not self.remaining_pieces:
      yield self.board.copy()
    else:
      pos = self.next_pos()
      for name in self.remaining_pieces.copy():
        index = self.piece_idx[name]
        for xy in self.orientations[index]:
          xy = xy + pos
          if not self.can_place(xy):
            continue
          self._place(xy, index)
          self.remaining_pieces.remove(name)
          for solution in self.solutions():
            yield solution
          self._place(xy, 0)
          self.remaining_pieces.append(name)

  def solve(self) -> None:
    """Sets the board to the next found solution."""
    self.board = next(self.solutions())
    self.remaining_pieces = []


def all_3d_rotations_and_translations(definition: List[Tuple[int, int]]
    ) -> List[np.ndarray]:
  """All possible displacements of a piece which contain (0, 0, 0)."""
  result_2d = all_2d_rotations_and_translations(definition)
  # Pieces are either horizontal, or in one of two vertical planes.
  result = [xy @ np.array([[1, 0, 0], [0, 1, 0]]) for xy in result_2d]
  result.extend([xy @ np.array([[0, -1, 1], [-1, 0, 1]]) for xy in result_2d])
  result.extend([xy @ np.array([[0, 0, 1], [-1, -1, 1]]) for xy in result_2d])
  return result


def pyramid_board():
  board = np.zeros((5, 5, 5), dtype='uint8')
  for z in range(1, 5):
    board[-z:, :, z] = -1
    board[:, -z:, z] = -1
  return board


class Lonpos3D:
  """A Lonpos solver for the pyramid."""

  def __init__(self):
    self.piece = {i + 1: p for i, p in enumerate(PIECES)}
    self.piece_idx = {p.name: i for i, p in self.piece.items()}
    orientations = {}
    for i, piece in self.piece.items():
      coord_list = all_3d_rotations_and_translations(piece.definition)
      orientations[i] = tuple(np.array(coords) for coords in coord_list)
    self.orientations = orientations
    self.set_board(pyramid_board())

  def __repr__(self):
    return 'Lonpos3D()'


  def set_board(self, board: np.ndarray) -> None:
    """Sets a board position."""
    self.board = board.copy()
    used_indices = np.unique(board)
    self.remaining_pieces = [p.name for i, p in self.piece.items()
                                 if i not in used_indices]

  def completed(self) -> bool:
    """True if the board is completed."""
    return len(self.remaining_pieces) == 0 and (self.board != 0).all()


  def in_bounds(self, x: int, y: int, z: int) -> bool:
    return (0 <= x < self.board.shape[0] and
            0 <= y < self.board.shape[1] and
            0 <= z < self.board.shape[2])


  def next_pos(self) -> Tuple[int, int]:
    """A good candidate position on the board to try to fill."""
    # Returns an empty spot with few-ish empty neighbors.
    candidate = None
    candidate_neighbors = 12
    empty = [(x, y, z) for x in range(self.board.shape[0])
                 for y in range(self.board.shape[1])
                 for z in reversed(range(self.board.shape[2]))  # top first
                 if not self.board[x, y, z]]
    offsets = [(1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0),
               (-1, -1, 1), (-1, 0, 1), (0, -1, 1), (0, 0, 1),
               (-1, -1, -1), (-1, 0, -1), (0, -1, -1), (0, 0, -1)]
    for p in empty:
      nbrs = [(p[0] + i, p[1] + j, p[2] + k) for i, j, k in offsets]
      nbrs = [n for n in nbrs if self.in_bounds(n[0], n[1], n[2])]
      num_neighbors = sum(n in empty for n in nbrs)
      if num_neighbors in [0, 1, 2]:
        # Good enough.
        return p
      if candidate is None or num_neighbors < candidate_neighbors:
        candidate = p
        candidate_neighbors = num_neighbors
    return candidate


  def can_place(self, xyz: np.ndarray) -> bool:
    return (all(self.in_bounds(x, y, z) for x, y, z in xyz) and
            not self.board[xyz[:, 0], xyz[:, 1], xyz[:, 2]].any())


  def _place(self, xyz: np.ndarray, index: int) -> None:
    self.board[xyz[:, 0], xyz[:, 1], xyz[:, 2]] = index


  def place(self, name: str, xyz: np.ndarray) -> None:
    """Adds the given piece to the board at the given coordinates."""
    assert name in self.remaining_pieces, f'piece {name} not available'
    index = self.piece_idx[name]
    valid_xyz = set(normalized_tuple(xyz_) for xyz_ in self.orientations[index])
    assert normalized_tuple(xyz - xyz[0]) in valid_xyz, (
        f'Not a valid orientation of piece {name}:\n{xyz}')
    assert self.can_place(xyz), f'cannot place at {xyz}'
    self._place(xyz, self.piece_idx[name])
    self.remaining_pieces.remove(name)


  def get_xyz(self, name):
    """Returns the coordinates of a piece on the board."""
    index = self.piece_idx[name]
    if not (self.board == index).any():
      raise ValueError(f'{name} is not on the board')
    x, y, z = (self.board == index).nonzero()
    return np.array(list(zip(x, y, z)))


  def unplace(self, *names):
    """Removes the given pieces from the board."""
    for name in names:
      xyz = self.get_xyz(name)
      self._place(xyz, 0)
      self.remaining_pieces.append(name)


  def drawn_position(self, x, y, z):
    """The 2D position of a 3D location for display purposes."""
    xx = (x + .5 * z)
    yy = (0.7 * y + (4.5 - .3 * z) * z)
    return xx, yy


  def plot(self, board: Optional[np.ndarray] = None, ax=None) -> None:
    """Displays the board."""
    if board is None:
      board = self.board
    if ax is None:
      plt.figure(figsize=(2.5, 6))
      ax = plt.gca()
    ax.set_xlim(-.6, board.shape[0] - .4)
    ax.set_ylim(-.6, self.drawn_position(0, 0, board.shape[2] - 1)[1] + .6)
    ax.set_aspect('equal')
    ax.axis('off')
    for z in range(board.shape[2]):
      for y in reversed(range(board.shape[1])):  # draw back bubbles first
        for x in range(board.shape[0]):
          idx = board[x, y, z]
          xx, yy = self.drawn_position(x, y, z)
          if idx == 255:
            pass
          elif idx:
            piece = self.piece[idx]
            ax.add_patch(plt.Circle((xx, yy), 0.5, facecolor=piece.color,
                edgecolor='black', clip_on=False))
            ax.text(xx, yy, piece.name, ha='center', va='center')
          else:
            ax.add_patch(plt.Circle((xx, yy), 0.3, color='lightgray',
                clip_on=False))


  def solutions(self) -> Iterator[np.ndarray]:
    """All solutions from the given position."""
    if not self.remaining_pieces:
      yield self.board.copy()
    else:
      pos = self.next_pos()
      for name in self.remaining_pieces.copy():
        index = self.piece_idx[name]
        for xyz in self.orientations[index]:
          xyz = xyz + pos
          if not self.can_place(xyz):
            continue
          self._place(xyz, index)
          self.remaining_pieces.remove(name)
          for solution in self.solutions():
            yield solution
          self._place(xyz, 0)
          self.remaining_pieces.append(name)


################################################################################
# A-puzzle-a-day calendar: https://www.dragonfjord.com/product/a-puzzle-a-day  #
################################################################################

def calendar_pieces():
  pieces = [p for p in PIECES if p.name in ['B', 'C', 'D', 'E', 'G', 'I']]
  pieces += [
      Piece('Z', 'orange', ((0, 0), (1, 0), (1, 1), (1, 2), (2, 2))),
      Piece('O', 'magenta', ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)))
  ]
  return pieces

def calendar_board_text():
  txt = np.concatenate(
    [np.array([['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', ''],
               ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', '']]),
     np.array([str(x) for x in range(1, 36)]).reshape((5, 7))], axis=0)
  txt[-1, -4:] = ''
  txt = np.rot90(txt, -1)
  return txt

def calendar_board(month, day):
  month = str(month)
  month = month[0].upper() + month[1:3]
  txt = calendar_board_text()
  board = np.zeros(txt.shape, dtype='uint8')
  board = np.where(txt == '', -1, board)
  board = np.where(txt == month, -1, board)
  board = np.where(txt == str(day), -1, board)
  return board.astype('uint8')

class Calendar(Lonpos2D):
  def __init__(self, month, day):
    self.piece = {i + 1: p for i, p in enumerate(calendar_pieces())}
    self.piece_idx = {p.name: i for i, p in self.piece.items()}
    orientations = {}
    for i, piece in self.piece.items():
      coord_list = all_2d_rotations_and_translations(piece.definition)
      orientations[i] = tuple(np.array(coords) for coords in coord_list)
    self.orientations = orientations
    self.set_board(calendar_board(month, day))
    self.board_text = calendar_board_text()
    self.month = month
    self.day = day

  def __repr__(self):
    return f'Calendar({self.month!r}, {self.day!r})'

  def plot(self, board: Optional[np.ndarray] = None, ax=None) -> None:
    """Displays the board."""
    if ax is None:
      ax = plt.gca()
    if board is None:
      board = self.board
    ax.set_facecolor('lightgray')
    ax.set_xlim(-.6, board.shape[0] - .4)
    ax.set_ylim(-.6, board.shape[1] - .4)
    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    for x in range(board.shape[0]):
      for y in range(board.shape[1]):
        idx = board[x, y]
        if idx == 255:
          text = self.board_text[x, y]
          if text:
            ax.text(x, y, self.board_text[x, y], ha='center', va='center')
          else:
            ax.add_patch(plt.Rectangle((x-.4, y-.4), .8, .8, color='white',
                clip_on=False))
        elif idx:
          piece = self.piece[idx]
          ax.add_patch(plt.Rectangle((x-.5, y-.5), 1, 1, facecolor=piece.color,
              clip_on=False))
          ax.text(x, y, piece.name, ha='center', va='center', c='grey')
