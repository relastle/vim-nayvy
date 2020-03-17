"""
Python sample module which

- has many unnecessary imports
- has many undefined names (requiring imports)

"""

import os
import subprocess
import multiprocessing


def main() -> None:
    # undefine np (which requires `import numpy as np`)
    arr = np.array([1, 2, 3])
    # undefined pp (which requires `from pprint import pprint as pp)
    pp(arr)
    # undefined top_level_function1 (which requires import whithin project)
    _ = top_level_function1()
    # undefined sys (which requires 'import sys')
    sys.exit(1)


if __name__ == '__main__':
    main()
