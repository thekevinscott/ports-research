import json
import os
import sys
from typing import Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def cases(name: str) -> List[Any]:
    """The cases from the generated TypeScript suite, as extracted into `data/`."""
    with open(os.path.join(DATA, f'{name}.json'), encoding='utf-8') as handle:
        return json.load(handle)
