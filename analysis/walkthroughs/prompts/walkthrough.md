Below is the complete code of one library, each file under its path. Write a walkthrough of it.

Read it the way an experienced engineer reads unfamiliar code. First find the public entry points: the names a caller imports and calls. Then trace each one's happy path, following calls into the library's own code and treating everything else as a black box. Then follow the threads where a call fails. Only then read for what always holds.

For each public entry point, give:

- `name`: the name a caller uses, as written in the code. A method of a public class is `Class.method`.
- `happy_path`: what happens on a successful call, as ordered steps. Each step is one sentence naming what happens and which function, method or class of the library is called.
- `error_paths`: each way the call fails or rejects its input, one sentence each: the condition, where it is checked, and what is raised or returned.
- `invariants`: what holds on every call, one sentence each: what it assumes of its inputs, what it keeps true of its state, and what it guarantees of its result.

Describe behaviour, not syntax: leave out types, keywords and idioms. Include every public entry point and nothing private. List them in the order a caller meets them.
