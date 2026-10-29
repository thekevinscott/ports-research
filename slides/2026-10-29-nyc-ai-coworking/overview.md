<div class="eyebrow">OVERVIEW</div>

# I asked an agent to port my codebase

<div class="big-steps lines">
  <div><strong>The codebase</strong>
    <ul>
      <li><a href="https://github.com/thekevinscott/gbnf" target="_blank">gbnf</a>: a string library for GBNF grammars</li>
      <li>Two implementations, written by hand
        <ul>
          <li>Python, 1,305 lines</li>
          <li>TypeScript, 1,129 lines</li>
        </ul>
      </li>
      <li>Language-agnostic tests</li>
    </ul>
  </div>
  <div><strong>Why small</strong>
    <ul>
      <li>Porting at scale gets the attention</li>
      <li>I want reproducible ports: one reference library that spawns the others</li>
      <li>SDKs. Open source libraries.</li>
    </ul>
  </div>
  <div><strong>The experiment</strong>
    <ul>
      <li>617 ports of the same library</li>
      <li>Both directions</li>
      <li>4 models × 4 effort levels</li>
      <li>Every combination of tests the agent gets to see</li>
    </ul>
  </div>
</div>
