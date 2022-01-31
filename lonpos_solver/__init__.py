from typing import List, Tuple, 
import numpy as np
import dataclasses


@dataclasses.dataclass
class Piece:
  name: str
  color: str
  definition: List[Tuple[int, int]]

PIECES = (
    Piece(name='A', color='orange', definition=((0, 0), (1, 0), (1, 1), (1, 2))),
    Piece(name='B', color='red', definition=((0, 0), (0, 1), (1, 0), (1, 1), (1, 2))),
    Piece(name='C', color='blue', definition=((0, 0), (1, 0), (1, 1), (1, 2), (1, 3))),
    Piece(name='D', color='pink', definition=((0, 0), (1, 0), (1, 1), (1, 2), (1, -1))),
    Piece(name='E', color='green', definition=((0, 0), (0, 1), (1, 1), (1, 2), (1, 3))),
    Piece(name='F', color='whitesmoke', definition=((0, 0), (1, 0), (1, 1))),
    Piece(name='G', color='cyan', definition=((0, 0), (1, 0), (2, 0) ,(2, 1), (2, 2))),
    Piece(name='H', color='magenta', definition=((0, 0), (1, 0), (1, 1) ,(2, 1), (2, 2))),
    Piece(name='I', color='yellow', definition=((0, 0), (0, 1), (1, 0), (2, 0) ,(2, 1))),
    Piece(name='J', color='darkviolet', definition=((0, 0), (0, 1), (0, 2), (0, 3))),
    Piece(name='K', color='lime', definition=((0, 0), (0, 1), (1, 0), (1, 1))),
    Piece(name='L', color='gray', definition=((0, 0), (1, 0), (1, 1), (1, -1), (2, 0))),
)

def normalized_tuple(coords: np.ndarray) -> Tuple[Tuple[int]]:
  """A hashable (uniquified) representation of a set of coordinates."""
  return tuple(sorted(tuple(p) for p in coords))

def all_2d_rotations_and_translations(definition: Tuple[Tuple[int]]):
  rot90 = np.array([[0, -1], [1, 0]])
  flip = np.array([[-1, 0], [0, 1]])
  xys = []
  coords = np.array(definition)
  for _ in range(2):
    for _ in range(4):
      for offset in coords:
        xys.append(coords - offset)
      coords = coords @ rot90
    coords = coords @ flip
  return [np.array(xy) for xy in set(normalized_tuple(p) for p in xys)]



# TODO: Factor out board logic, so that this class can be initialized with
# different boards.
class RectangleGame:

  def __init__(self):
    self.board = board = np.zeros((5, 11), dtype=np.uint8)
    self.all_pieces = [Piece(name='', color='black', definition=[(0, 0)])] + list(PIECES)
    self.remaining_pieces = list(range(1, len(self.all_pieces)))

    orientations = []
    for piece in self.all_pieces:
      coord_list = all_2d_rotations_and_translations(piece.definition)
      orientations.append(tuple(np.array(coords) for coords in coord_list))
    self.orientations = orientations

  def completed(self):
    return len(self.remaining_pieces) == 0 and (self.board != 0).all()

  def next_pos(self):
    # Return an empty spot with 1 neighbor if possible, 2 neighbors otherwise
    candidate = None
    empty = [(x, y) for x in range(11) for y in range(5) if not self.board[y, x]]
    offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for p in empty:
      nbrs = [(p[0] + i, p[1] + j) for i, j in offsets]      
      nbrs = [n for n in nbrs if 0 <= n[0] < 11 and 0 <= n[1] < 5]
      num_neighbors = sum(n in empty for n in nbrs)
      if num_neighbors in [0, 1]:
        return p
      elif num_neighbors == 2 and candidate is None:
        candidate = p
    return candidate

  def can_place(self, xy):
    return (all(0 <= x < 11 for x in xy[:, 0]) and
            all(0 <= y < 5 for y in xy[:, 1]) and
            not self.board[xy[:, 1], xy[:, 0]].any())

  def _place(self, xy, index) -> None:
    self.board[xy[:, 1], xy[:, 0]] = index

  def place(self, xy, index) -> None:
    if index > 0:
      assert index in self.remaining_pieces, f'piece {self.all_pieces[index].name} not available'
      assert self.can_place(xy), f'cannot place at {xy}'
      self._place(xy, index)
      self.remaining_pieces.remove(index)
    else:
      vals = self.board[xy[:, 1], xy[:, 0]]
      removed_index = vals[0]
      assert (vals == removed_index).all(), f'{xy} not occupied by single piece'
      self._place(xy, 0)
      self.remaining_pieces.append(removed_index)


  def plot(self, board=None, ax=None):
    if ax is None:
      ax = plt.gca()
    if board is None:
      board = self.board
    ax.set_facecolor('black')
    ax.set_xlim(-.5, 10.5)
    ax.set_ylim(-.5, 4.5)
    ax.set_aspect('equal')
    for x in range(11):
      for y in range(5):
        idx = board[y, x]
        if idx:
          piece = self.all_pieces[idx]
          ax.add_patch(plt.Circle((x, y), 0.5, color=piece.color, clip_on=False))
          ax.text(x, y, piece.name, ha='center', va='center')    


  def solutions(self) -> Iterator[np.ndarray]:
    if not self.remaining_pieces:
      yield self.board.copy()
    else:
      pos = self.next_pos()
      for piece_idx in self.remaining_pieces.copy():
        for xy in self.orientations[piece_idx]:
          xy = xy + pos
          if not self.can_place(xy):
            continue
          self._place(xy, piece_idx)
          self.remaining_pieces.remove(piece_idx)
          for solution in self.solutions():
            yield solution
          self._place(xy, 0)
          self.remaining_pieces.append(piece_idx)

# TODO: Add 3D game
