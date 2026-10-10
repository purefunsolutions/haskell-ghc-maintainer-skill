# gitlab.haskell.org without a token

Sources: <https://docs.gitlab.com/api/> (issues, merge requests, pipelines, jobs), and behaviour
observed on 2026-10-10.

- API base: `https://gitlab.haskell.org/api/v4`. `ghc/ghc` is project `1`. A fork has its own ID
  (the MR's `source_project_id`); URL-encoded paths such as `mikatammi%2Fghc` also work.
- Bot protection (Anubis): browser-like User-Agents get a challenge page. Plain `curl` with its
  default User-Agent gets through, both for the API and for wiki pages as raw markdown
  (`https://gitlab.haskell.org/ghc/ghc/-/wikis/<page>.md`).
- **No token needed:** searching and reading issues and MRs, MR pipelines, the jobs of a
  pipeline, and job logs via the web URL `<job URL>/raw`. That URL redirects to object storage,
  so use `curl -L`.
- **Token needed:** labels, milestones, issue and MR discussions (notes), the job trace API. Ask
  the user to paste discussions, or to call the API with their own token in their own terminal,
  so the token stays out of the agent's transcript.

## Recipes

    api=https://gitlab.haskell.org/api/v4/projects/1
    curl -sS -G "$api/issues" --data-urlencode "search=<term>"          # all states by default
    curl -sS -G "$api/merge_requests" --data-urlencode "search=<term>" --data-urlencode state=all
    curl -sS "$api/issues/<N>"
    curl -sS "$api/merge_requests/<N>"            # labels, sha, source_project_id
    curl -sS "$api/merge_requests/<N>/pipelines"  # includes pipelines run in the fork
    curl -sS "https://gitlab.haskell.org/api/v4/projects/<pid>/pipelines/<id>/jobs?per_page=100"
    curl -sS -G "$api/merge_requests" --data-urlencode "labels=backport needed:10.0" --data-urlencode state=all
    curl -sS -G "$api/merge_requests" --data-urlencode "author_username=<user>" --data-urlencode state=all

## From a commit to its MR

`/repository/commits/<sha>/merge_requests` comes back empty for commits that marge-bot merged:
it rebases and merges through batch MRs, and the original MR then shows "closed". Search MR
titles for the commit subject instead, or search by author plus a keyword. The MR's discussion
has marge-bot's "Merged in <sha>" comment.
