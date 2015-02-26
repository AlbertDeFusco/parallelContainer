# parallelContainer

Exploratory project to wrap mpi4py communcation in a new distributed
container. charm++ is considered to be an inspiration. (http://charm.cs.illinois.edu/research/charm)
This project was initiated through discussion with Esteban Meneses (http://coco.sam.pitt.edu/~emeneses/)

Goals:
 - Create a new list-like container that
   1. distribute one item per rank when calling parList.append()
   2. hack __getitem__ to facilitate mpi communication between items
   3. transfer information between items with member functions
   4. Implement mpi reduction to allow sum(parList) through __add__ and __radd__
