This is about solving [these puzzles](https://www.lonpos.com.au). Like many
people before me, I felt I had to write a little program to find solutions. If
you're reading this, you're probably one of those people too.

This implementation is a straightforward DFS in which we identify an empty spot
with as few empty neighbors as possible, and try all possible ways to fill that
spot. This is basically the strategy I find myself using when I do these
things, and it seems pretty good (i.e. it identifies dead ends pretty quickly).

See [Lonpos_solver_demo.ipynb](Lonpos_solver_demo.ipynb) for some pretty
pictures.
