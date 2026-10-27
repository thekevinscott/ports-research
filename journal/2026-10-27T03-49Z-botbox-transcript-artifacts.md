# 2026-10-27 03:49Z — botbox transcript artifacts were lost

The subscription-auth `gbnf_experiment` e2e run after botbox 0.1.72 wrote both a session JSONL and a `tool-results/*.txt` file under botbox's `transcripts/` directory. The existing banker moved only regular JSONL files into the run record, then deleted the rest of the tree. The tool result was absent from the completed run folder.

Issue #242 follows up on the finding. A named unit test first reproduced the loss with a non-JSONL file; the banker now moves the whole transcript tree as-is. The post-fix real e2e passed and retained botbox's directory structure. No gbnf reference source was changed.
