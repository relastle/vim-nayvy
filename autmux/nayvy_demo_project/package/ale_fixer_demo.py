"""
Python sample module which

- has many unnecessary imports
- has many undefined names (requiring imports)

"""

# Unused imports and inappropriate import orders
# (should be fixed by nayvy and isort)

import os
import subprocess
import multiprocessing

import sys

class Hoge:
    def __init__(self) -> None:
        '''
        Description of initializer

        '''
        return

def main() -> None:
    """
    """



    # undefine np (which requires `import numpy as np`)
    arr = np.array([1, 2, 3])
    # undefined pp (which requires `from pprint import pprint as pp)
    pp(arr)
    # undefined top_level_function1 (which requires import whithin project)
    _ = top_level_function1()
    # undefined sys (which requires 'import sys')
    sys.exit(1)




# inappropriate many line breaks (should be fixed by autopep8)




if __name__ == '__main__':
    main()
