<div class="eyebrow">METHODOLOGY · CONTAINER AND PROMPT</div>

# What the agent gets

<div class="prompt-layout">
  <div class="prompt-col">
    <div class="prompt-label">The container</div>
    <ul class="prompt-notes">
      <li>Locked-down Docker container</li>
      <li>No network other than LLM endpoints. No npm, no PyPI: gbnf is published on both.</li>
      <li>pytest, vitest, uv, pnpm pre-installed</li>
    </ul>
    <div class="prompt-label">On disk</div>
<pre class="prompt-tree">/input/     the reference, read-only
  python/gbnf/              35 files
  python/tests/generated/    5 files
/target/    empty</pre>
  </div>
  <div class="prompt-col">
    <div class="prompt-label">Prompt †</div>
<pre class="prompt-text">You are porting software from one language to another.
&nbsp;
The reference is mounted at `/input`.
&nbsp;
Write the port to `/target`.
&nbsp;
The library itself may specify additional porting instructions below. Paths in them are relative to `/input`.
&nbsp;
Port the implementation under <mark>python/</mark> to <mark>typescript</mark>.
There is no network access. uv, pytest, pnpm and vitest are installed.
&nbsp;
<mark>The following test suites are included:</mark>
&nbsp;
<mark>- python integration tests: python/tests/generated/</mark></pre>
  </div>
</div>

<div class="source"><mark>*</mark> yellow = varies per run: the source directory, the target language, and which test suites the agent is told it has. Everything else is identical across all 617 runs.<br>† Verbatim from run 20261012T021310Z_595388f6 (python → typescript, source integration tests on), the prompt the 192 tests-configuration runs received. Later runs got a longer one: the reference is marked read-only and the two Dockerfiles the sandbox image was built from are pasted in.</div>
