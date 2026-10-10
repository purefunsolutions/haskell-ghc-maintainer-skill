# GHC's LLM policy, applied

Source: <https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/AI> ("GHC Policy on LLM
contributions"; append `.md` to the URL for the raw text). Contributing-a-Patch §2.0 links it,
and it covers tickets, MRs, commits and reviews. "LLM" includes agentic AI.

## The rules (paraphrased; re-read the source when in doubt)

- **P1 People first.** In a conversation with a reviewer, the human must not relay AI-generated
  text as a substitute for their own judgement. Brief, signposted quotes are fine.
- **P2 Easy to review.** A clear goal, small digestible pieces, tests where possible. The
  contributor puts in more effort than the reviewer has to.
- **P3 Human authorship.** A human author takes full responsibility for every line of code and
  every sentence of documentation, and must be able to explain all of it. LLM "drive-by" MRs
  are never OK. A draft MR may be fully LLM-generated if it's marked Draft and says at the top
  that review isn't sought yet.
- **P4 Declare.** If an LLM generated any part of the contribution, say so up front: in the
  issue or MR description, and in the commit message, "usually by adding a line
  `Assisted-By: <tool>`". State that the material was reviewed and that the human takes
  responsibility. Declaring use for research or debugging is encouraged, not required.
- **R1 Write the final version yourself.** A strong recommendation, not a rule. The named
  exception is an obviously correct one-line fix. The policy also cites copyright: GNU's
  threshold of about 15 legally significant lines.

## What this means for you, the agent

- Keep code changes minimal and prose short. That keeps P3 and R1 cheap for the human.
- Draft texts as plain, factual, paste-ready notes that the human can adopt or rewrite. The
  disclosure sentence ("I have carefully reviewed…") is the human's to make. Never claim it on
  their behalf, and remind them to review before posting.
- Commit trailer, in the last paragraph of the message:

      Assisted-by: <tool> (<model>)

  For example `Assisted-by: Claude Code (Claude Opus 5.5)`. GHC master has many such trailers,
  e.g. `234bab0816` (`Assisted-by: Claude Opus 5`) and `4cf7628aa6` (`Assisted-By: OpenAI Codex`).
  Prefer it over `Co-authored-by`, which credits the tool as an author and so runs against P3.
- First line of an issue or MR description:

      _LLM assistance: <tool> (<model>) was used to investigate this and to draft this report. I have carefully reviewed and revised it and take responsibility for it under [P3](https://gitlab.haskell.org/ghc/ghc/-/wikis/contributing/AI)._

- In review threads, help the human understand comments, but don't write replies for them to
  paste.
- GHC doesn't use a DCO, and `Signed-off-by` is optional and rare there. Never add one for the
  user; they can add it themselves with `git commit -s`.
