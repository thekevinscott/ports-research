import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Judging fidelity: techniques on the table

    2026-10-12

    Kevin: "I'd like to high level discuss analysis. Specifically how to do the judging. We'd mentioned running the test suite: measuring edit distance; embedding distance; and LLM judge. Were there any other techniques we discussed for fidelity"

    The four he named: test-suite pass rate; edit distance; embedding distance; LLM judge. The rest follow, grouped by status: built, decided but not built, literature only.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Built

    ### Held-out behavioral agreement

    [analysis/measure-behavior](../measure-behavior/README.md), [PR #118](https://github.com/thekevinscott/ports-research/pull/118). A generated corpus of 100 grammars and 799 inputs (seed 0), never mounted into the agent's container, runs through the reference and through the port. Each pair's outcome is accept, reject, error or crash. Output is an agreement rate and a confusion table of reference outcome × port outcome.

    ### Differential API exercise

    [analysis/exercise-api](../exercise-api/README.md). Per case: construct the grammar, add the input, compare the resulting rule objects with the reference's as a set. Wall time per case, reported as mean, p50 and p95. Cases come from hypothesis generation (seed 0, 500 cases) and from the reference integration suite's fixtures (453 cases).

    Kevin, 2026-09-16: "exercise-api to v3. I still feel of the mind to drop it and start fersh."

    ### AST and structural measures

    [analysis/measure-ast](../measure-ast/README.md), [analysis/measure-embedding](../measure-embedding/README.md). The v2 plan, 2026-09-16: seven AST measures including cyclomatic complexity are computed for every run and displayed nowhere; the notebook shows only file count and LOC.

    Kevin: "I'm still not sure how to interpret any of the AST stuff"

    The code-embeddings literature review found embeddings track surface similarity, not correctness, and recommended calling the measure structural drift. The shipped measure is a per-file Chamfer distance taken in both directions, comments stripped, no identifier normalization ([EMBEDDINGS.md](EMBEDDINGS.md)).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Decided, not built

    ### Internal-state parity script

    From [Mistral's legacy modernization post](https://mistral.ai/news/legacy-code-modernization/): an automated script asserting that internal state matches, not only outputs. Kevin, 2026-09-16: "building an _automated_ testing script asserting the internal state, which is a fantastic idea, but out of scope." A v3 candidate next to the fidelity scale.

    ### Fidelity scale

    Kevin, an earlier ask recorded in the v2 plan: "what I want is a way to say 'this port is extremely faithful, basically an exact copy'". Measured in scratch, nothing landed.

    Kevin, 2026-09-16: "A better understanding of what faithful means - totally want to dig in on this. this feels like a v3 thing though. My hope is that the initial experiment reveals some directions in which to go."

    ### Grader validation by mutation

    Copy the reference to scratch, mutate it a handful of ways (flip an operator, drop a branch, shift a bound), run the derived suite against each mutant, and record which mutants it catches and which survive. Proposed by the agent, adopted by Kevin 2026-09-16: "'validate the grader' - equally good! phenomenal idea. same thing." The grader was taken off the V2 path on 2026-10-12.

    ### Post-hoc cheating judge

    A stronger model reads each banked transcript, not the code, against a fixed written rubric of what counts as cheating. The rubric is written before the first run is read; every run is scored; uncertain runs go to Kevin. Kevin, 2026-09-16: "I love your counter proposal on my check-in! Yes absolutely."
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Literature only

    From [literature/SYNTHESIS.md](../../literature/SYNTHESIS.md):

    - Property-based testing and metamorphic relations.
    - Differential symbolic execution (RustAssure).
    - Doc-as-spec with LLM-judged feature preservation (RustPrint).
    - A security gate: differential testing with adversarial inputs first, SAST second, LLM judge advisory.

    Training-data contamination: `contamination-probe`, Python side only, never used in a banked run, was deleted in #68 ([journal](../../journal/2026-09-26T22-30Z-repo-laid-out-as-porting-and-analysis.md)).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Tests as the judge

    Kevin, 2026-09-16: "I think it's very naive to say 'can it pass the provided tests'. One, I think most software is not tested or not well tested. Two, I think it's a bit of a red herring; my use case would not be asking the agent to do its work with a hand tied behind its back, if tests are available then the agent should use them! Third, I think the more interesting question is the faithfulness / fidelity one, and tests I don't think really answer that - with teh strong exception of what I skimmed from Mistral's post, about building an _automated_ testing script asserting the internal state, which is a fantastic idea, but out of scope."

    Sources: [notes/PLAN_2026-09-16-v2.md](../../notes/PLAN_2026-09-16-v2.md), [journal/](../../journal/README.md).
    """)
    return


if __name__ == "__main__":
    app.run()
