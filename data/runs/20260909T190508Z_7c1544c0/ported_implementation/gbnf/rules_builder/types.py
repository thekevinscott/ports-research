from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


class InternalRuleType(str, Enum):
    CHAR = 'CHAR'
    CHAR_RNG_UPPER = 'CHAR_RNG_UPPER'
    RULE_REF = 'RULE_REF'
    ALT = 'ALT'
    END = 'END'

    CHAR_NOT = 'CHAR_NOT'
    CHAR_ALT = 'CHAR_ALT'


# CHAR and CHAR_NOT carry a list of code points; RULE_REF, CHAR_ALT and
# CHAR_RNG_UPPER carry a single number; ALT and END carry nothing.
InternalRuleValue = Optional[Union[int, List[int]]]


@dataclass
class InternalRuleDef:
    type: InternalRuleType
    value: InternalRuleValue = field(default=None)
