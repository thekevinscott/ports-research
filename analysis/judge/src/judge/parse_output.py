import json


def parse_output(stdout: str) -> dict:
    """The verdicts, raw text and usage from the claude CLI's JSON output.

    The verdicts are the schema-constrained structured output, or else the first JSON object in the text.
    """
    output = json.loads(stdout)
    raw = output.get("result")
    if output.get("is_error"):
        raise ValueError(f"the CLI reported an error: {raw}")
    verdicts = output.get("structured_output")
    if verdicts is None:
        decoder = json.JSONDecoder()
        for start in (i for i, c in enumerate(raw or "") if c == "{"):
            try:
                verdicts, _ = decoder.raw_decode(raw, start)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"no JSON object in the result: {raw!r}")
    return {"verdicts": verdicts, "raw": raw, "usage": output.get("usage")}
