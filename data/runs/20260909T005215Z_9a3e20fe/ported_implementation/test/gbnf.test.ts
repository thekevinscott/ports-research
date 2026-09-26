import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { GBNF } from '../src/index.ts';
import { GrammarParseError, InputParseError } from '../src/index.ts';

/**
 * End-to-end fixtures captured from `reference_implementation` — for every
 * grammar below, each entry in `steps` is the set of rules the reference
 * implementation reports before consuming the corresponding input character.
 */
interface Step {
  rules?: { type: string; value?: (number | number[])[] }[];
  error?: string;
}

interface Case {
  grammar: string;
  inputs: string[];
  steps?: Step[];
  error?: string;
}

const CASES: Case[] = [
  {
    "grammar": "root ::= \"foo\"",
    "inputs": [
      "f",
      "o",
      "o"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              102
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              111
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              111
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= [a-z]+",
    "inputs": [
      "a",
      "b",
      "z"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"a\" | \"b\"",
    "inputs": [
      "a"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= [^a-z]",
    "inputs": [
      "A"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleCharExclude",
            "value": [
              [
                97,
                122
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= ws \"hi\"\nws ::= [ \\t]*",
    "inputs": [
      " ",
      "h",
      "i"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              104
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              32,
              9
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              104
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              32,
              9
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              105
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= (\"a\" | \"b\")* \"c\"",
    "inputs": [
      "a",
      "b",
      "c"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              99
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              99
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              99
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"a\"? \"b\"",
    "inputs": [
      "b"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= [0-9] [0-9]",
    "inputs": [
      "1",
      "2"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root  ::= (expr \"=\" ws term \"\\n\")+\nexpr  ::= term ([-+*/] term)*\nterm  ::= ident | num | \"(\" ws expr \")\" ws\nident ::= [a-z] [a-z0-9_]* ws\nnum   ::= [0-9]+ ws\nws    ::= [ \\t\\n]*",
    "inputs": [
      "a",
      "+",
      "1",
      "=",
      "2",
      "\n"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              40
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              32,
              9,
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              45,
              43,
              42,
              47
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              61
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ],
              [
                48,
                57
              ],
              95
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              40
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              32,
              9,
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              45,
              43,
              42,
              47
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              61
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              32,
              9,
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              40
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              32,
              9,
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              32,
              9,
              10
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              40
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                48,
                57
              ]
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              [
                97,
                122
              ]
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"foo\"",
    "inputs": [
      "b"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              102
            ]
          }
        ]
      },
      {
        "error": "Failed to parse input string:\n\nb\n^"
      }
    ]
  },
  {
    "grammar": "root ::= bar",
    "inputs": [],
    "error": "Failed to parse grammar: Undefined rule identifier \"bar\"\n\nroot ::= bar\n         ^"
  },
  {
    "grammar": "root ::= ",
    "inputs": [],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"a\" \"b\" \"c\"",
    "inputs": [
      "a",
      "b",
      "c",
      "d"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              99
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "error": "Failed to parse input string:\n\nabcd\n   ^"
      }
    ]
  },
  {
    "grammar": "root ::= [\\x41-\\x5A]+",
    "inputs": [
      "A",
      "Z"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                65,
                90
              ]
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                65,
                90
              ]
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              [
                65,
                90
              ]
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"\\U0001F4A9\"",
    "inputs": [
      "💩"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              128169
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "# comment\nroot ::= \"a\" # trailing\n",
    "inputs": [
      "a"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"a\"*",
    "inputs": [
      "a",
      "a",
      "a"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= (\"a\")+ | (\"b\")+",
    "inputs": [
      "b",
      "b"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          },
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          },
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= [abc-]",
    "inputs": [
      "-"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97,
              98,
              99,
              45
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= \"tab\\there\"",
    "inputs": [
      "t",
      "a",
      "b",
      "\t"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              116
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              97
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              98
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              9
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              104
            ]
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= a\na ::= b\nb ::= \"z\"",
    "inputs": [
      "z"
    ],
    "steps": [
      {
        "rules": [
          {
            "type": "RuleChar",
            "value": [
              122
            ]
          }
        ]
      },
      {
        "rules": [
          {
            "type": "RuleEnd"
          }
        ]
      }
    ]
  },
  {
    "grammar": "root ::= *",
    "inputs": [],
    "error": "Failed to parse grammar: Expecting preceding item to */+/? at 9\n\nroot ::= *\n         ^"
  },
  {
    "grammar": "root := \"a\"",
    "inputs": [],
    "error": "Failed to parse grammar: Expecting ::= at 5\n\nroot := \"a\"\n     ^"
  }
];

/** Rule order is not part of the contract, so compare sorted serializations. */
const normalize = (rules: Iterable<{ toDict(): Record<string, unknown> } | object>): string[] =>
  [...rules]
    .map((rule) => JSON.stringify('toDict' in rule ? (rule as { toDict(): unknown }).toDict() : rule))
    .sort();

describe('GBNF end to end', () => {
  for (const { grammar, inputs, steps, error } of CASES) {
    it(`parses ${JSON.stringify(grammar).slice(0, 70)}`, () => {
      if (error !== undefined) {
        assert.throws(() => GBNF(grammar), (err: unknown) => {
          assert.ok(err instanceof GrammarParseError);
          assert.equal(err.message, error);
          return true;
        });
        return;
      }
      assert.ok(steps);
      let state = GBNF(grammar);
      assert.deepStrictEqual(normalize(state), normalize(steps[0].rules ?? []));
      for (let i = 0; i < inputs.length; i++) {
        const expected = steps[i + 1];
        if (expected === undefined) {
          break;
        }
        if (expected.error !== undefined) {
          assert.throws(() => state.add(inputs[i]), (err: unknown) => {
            assert.ok(err instanceof InputParseError);
            assert.equal(err.message, expected.error);
            return true;
          });
          break;
        }
        state = state.add(inputs[i]);
        assert.deepStrictEqual(normalize(state), normalize(expected.rules ?? []));
      }
    });
  }
});
