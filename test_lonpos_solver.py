"""An end-to-end test for lonpos_solver."""

import numpy as np
import lonpos_solver

NUM = 3

for board_type in ['rectangle', 'arrowhead', 'triangle', 'butterfly']:
  game = lonpos_solver.Lonpos2D(board_type)
  solns = []
  for b, i in zip(game.solutions(), range(NUM)):
    solns.append(b)
  assert len(solns) == NUM, (
      f'Failed to find {NUM} solutions for board shape "{board_type}"')
  print(f'Found {NUM} solutions for board shape "{board_type}"')


# Finding a solution from scratch takes much longer for the 3D version, so
# let's fill in a few pieces and check that we can find all the solutions.
game = lonpos_solver.Lonpos3D()
game.place('C', np.array(((0, 3, 0), (0, 4, 0), (1, 4, 0), (2, 4, 0), (3, 4, 0))))
game.place('E', np.array(((0, 2, 0), (1, 2, 0), (1, 3, 0), (2, 3, 0), (3, 3, 0))))
game.place('I', np.array(((0, 0, 0), (0, 1, 0), (1, 0, 0), (2, 0, 0), (2, 1, 0))))
game.place('F', np.array(((3, 2, 0), (4, 2, 0), (4, 3, 0))))
game.place('K', np.array(((3, 0, 0), (3, 1, 0), (4, 0, 0), (4, 1, 0))))
solns = list(game.solutions())
assert len(solns) == 2, 'Failed to find 2 solutions for the pyramid.'
print('Found 2 solutions for the pyramid, as expected.')
