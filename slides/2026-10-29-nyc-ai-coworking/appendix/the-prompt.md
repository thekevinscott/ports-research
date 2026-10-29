<div class="eyebrow">APPENDIX · THE PROMPT THE 413 MODEL × EFFORT RUNS GOT</div>

# The long prompt

<div class="prompt-layout">
<div class="prompt-col">
<pre class="prompt-text" style="font-size:10px;line-height:1.3;margin:0">You are porting software from one language to another.
The reference is mounted read-only at `/input`.
Write the port to `/target`.
There is no network access.
The sandbox image was built from these two Dockerfiles, the second on top of the first:
<span class="dim">[Dockerfile 1, 23 lines: node:24 base, Claude Code 2.1.296, socat, botbox-relay]</span>
<span class="dim">[Dockerfile 2, 20 lines: uv, Python 3.14.3, pytest, vitest, pnpm]</span>
The library itself may specify additional porting instructions below. Paths in them are relative to `/input`.
Port the implementation under python/ to typescript.
The following test suites are included:
- python unit tests: python/gbnf/ (colocated, *_test.py)
- python integration tests: python/tests/generated/</pre>
</div>
<div class="prompt-col">
<div class="prompt-label">Against the short one (slide 5)</div>
<ul class="prompt-notes">
<li>2,170 characters against about 450. The two Dockerfiles are 1,565 of them.</li>
<li>"mounted read-only" is new. The short prompt said only "mounted at /input".</li>
<li>"There is no network access" moved up; the tool list (uv, pytest, pnpm, vitest) left the prose for the Dockerfiles.</li>
<li>Two suites listed (unit, source integration) instead of one.</li>
<li>The Dockerfiles changed twice during the batch (botbox 0.0.20 → 0.1.1 → 0.1.72) and a memory cap was added; all three recorded in the experiment's DEVIATIONS.md.</li>
</ul>
</div>
</div>

<div class="source">Run 20261028-032612-bold-tooth (python → typescript), blank lines and Dockerfiles collapsed; full text in <code>public/long-prompt.txt</code><span class="date">2026-10-29</span></div>
