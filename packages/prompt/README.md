# prompt

A prompt template plus the values its slots take. `str(Prompt(template, **variables))` renders it; `template` is a string or a `Path` to read.

```python
from prompt import Prompt

str(Prompt("Port {source}/ to {target}.", source="python", target="javascript"))
```
