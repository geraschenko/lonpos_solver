import lonpos_solver
import matplotlib.pyplot as plt

NUM = 3

for board_type in ['rectangle', 'arrowhead', 'triangle', 'butterfly']:
  game = lonpos_solver.Lonpos2D(board_type)
  solns = []
  for b, i in zip(game.solutions(), range(NUM)):
    solns.append(b)
    # game.plot(b)
    # plt.show()
  assert len(solns) == NUM, (
      f'Failed to find {NUM} solutions for board shape "{board_type}"')
  print(f'Found {NUM} solutions for board shape "{board_type}"')
