"""A line-oriented JSON server exposing the `gbnf` package to the test bridge.

The generated test suite in `tests/` is written in TypeScript, so
`src/index.ts` drives this process over a pair of FIFOs. All grammar logic
lives in the Python package; this file only marshals values.

Protocol: one JSON request per line in, one JSON response per line out.

    {"id": 1, "op": "create", "grammar": "root ::= \\"foo\\"", "input": ""}
    {"id": 1, "ok": true, "state": 0, "rules": [{"type": "char", "value": [102]}]}
"""

import json
import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gbnf import GBNF, GrammarParseError, InputParseError, ParseState  # noqa: E402
from gbnf.grammar_graph.types import rule_to_dict  # noqa: E402

_states: List[ParseState] = []


def _store(state: ParseState) -> Dict[str, Any]:
    _states.append(state)
    return {
        'state': len(_states) - 1,
        'rules': [rule_to_dict(rule) for rule in state],
    }


def _handle(request: Dict[str, Any]) -> Dict[str, Any]:
    op = request['op']
    if op == 'create':
        return _store(GBNF(request['grammar'], request.get('input', '')))
    if op == 'add':
        return _store(_states[request['state']].add(request['input']))
    if op == 'size':
        return {'size': _states[request['state']].size}
    if op == 'grammar':
        return {'grammar': _states[request['state']].grammar}
    if op == 'input_error':
        error = InputParseError(
            request['mostRecentInput'], request['pos'], request['previousInput']
        )
        return {
            'message': error.message,
            'src': error.src,
            'errorForMostRecentInput': error.error_for_most_recent_input,
        }
    if op == 'grammar_error':
        error = GrammarParseError(
            request['grammar'], request['pos'], request['reason']
        )
        return {'message': error.message}
    raise Exception(f'Unknown op: {op}')


def main() -> None:
    if sys.argv[1:2] == ['--check']:
        # importing the package is the check; if we got here, it worked
        print('ok')
        return
    request_path, response_path = sys.argv[1], sys.argv[2]
    with open(request_path, 'r', encoding='utf-8') as requests, open(
        response_path, 'w', encoding='utf-8'
    ) as responses:
        for line in requests:
            line = line.strip()
            if not line:
                continue
            request = json.loads(line)
            response: Dict[str, Any] = {'id': request.get('id')}
            try:
                response.update({'ok': True, **_handle(request)})
            except InputParseError as err:
                response.update({
                    'ok': False,
                    'error': {
                        'name': 'InputParseError',
                        'message': err.message,
                        'args': [
                            err.most_recent_input,
                            err.pos,
                            err.previous_input,
                        ],
                    },
                })
            except GrammarParseError as err:
                response.update({
                    'ok': False,
                    'error': {
                        'name': 'GrammarParseError',
                        'message': err.message,
                        'args': [err.grammar, err.pos, err.reason],
                    },
                })
            except Exception as err:  # noqa: BLE001 - mirrored to the JS side
                response.update({
                    'ok': False,
                    'error': {'name': type(err).__name__, 'message': str(err)},
                })
            responses.write(json.dumps(response) + '\n')
            responses.flush()


if __name__ == '__main__':
    main()
