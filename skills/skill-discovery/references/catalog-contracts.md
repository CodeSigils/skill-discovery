# Catalog and source-search contracts

Prefer provider CLIs and documented APIs. Verify this file against provider
documentation when a query depends on exact authentication or response fields.

## Provider selection and fallback

### Remote source versus local cache

The local-first rule applies to installed and project skills. It does not make
an unverified checkout of an external catalog authoritative. Prefer the
provider's documented remote artifact or API at query time. If a checkout is
used as an offline or performance cache,
record all of the following independently:

- canonical remote URL and branch or artifact URL;
- local commit or file retrieval time;
- catalog generation timestamp from the artifact;
- remote comparison result (`matched`, `diverged`, or `unknown`);
- whether the search was completed remotely or from cache.

Use a read-only remote comparison when practical (for example, `git ls-remote`
or an HTTP GET of the documented artifact). Do not silently `pull`, `fetch`, or
rewrite the checkout as part of discovery. If comparison fails, continue with
reachable remote sources or report the catalog as unavailable; never convert a
cached empty result into evidence that no skill exists.

Do not query every provider for every request. Search applicable local roots
first, then choose the smallest useful set of external sources:

1. skills.sh directly when its installed CLI or authenticated API is available;
2. other documented catalogs or authenticated GitHub search for canonical source discovery;
3. browser or general web search as a final fallback.

Record each provider's timestamp, authentication state, result count, and failure
mode. Run independent lookups in parallel only when the additional coverage is
useful. Every serious result remains an untrusted pointer until its canonical
repository, exact revision, and complete payload are inspected.

## skills.sh

For interactive/local discovery, use an already-installed official CLI when one
is available. Check that the `skills` executable already exists before running
it. The commands below are examples, not permission to bootstrap a package
runner:

```bash
npx skills find '<query>'
npx skills add <owner/repository> --list
```

If `skills` is not already installed, prefer the read-only API below or another
documented fallback. Running `npx` for a missing CLI downloads and executes
external code and requires explicit user approval before discovery begins.

For an authorized broad search, `npx --yes skills find '<query>'` is a useful
retrieval path. Record the query timestamp, provider status, and full result
count separately from the small shortlist selected for inspection. Search terms
should include the user's wording and likely aliases. Treat result order,
install counts, and absence of a candidate as provisional retrieval signals;
they do not establish quality, compatibility, safety, or catalog completeness.
Use `npx --yes skills add <owner/repository> --list` or the source repository to
verify each candidate's canonical skill path before reading or recommending it.

### One-shot package runners

`uvx` is the Python-tool analogue of `npx`: it is an alias for `uv tool run`
and creates an isolated, temporary environment. [`pipx run`](https://pipx.pypa.io/latest/tutorial/run-applications.html)
is a comparable Python fallback. Neither runner can replace `npx` for the
Node-based Skills CLI. For JavaScript projects, `pnpm dlx` and `bunx` are
one-shot alternatives, but they remain provider-specific and should not be
added as runtime dependencies.

Mention these only as a soft suggestion when the user already uses the
corresponding ecosystem or `npx` is unavailable. Any one-shot runner downloads
and executes external code, so require the same explicit discovery authorization,
isolated working directory, version pinning where practical, and separate
installation/execution approval. Prefer an already-installed CLI or a
documented read-only API first.

Programmatic search uses the documented v1 endpoint:

```text
GET https://skills.sh/api/v1/skills/search?q=<query>&limit=<n>
Authorization: Bearer <Vercel OIDC token>
```

The response places results in `data`. Authentication and rate limits are part
of the contract; see <https://www.skills.sh/docs/api>. Do not rely on the legacy
unauthenticated `/api/search` endpoint even if it happens to respond.

Treat each result as an untrusted pointer. Before recommending it, resolve the
canonical repository, skill path, license, and exact reviewed commit from the
source repository. A missing token, unavailable API, stale index, or 404 detail
page is a source limitation to report—not evidence that no suitable skill
exists. Do not add a skills.sh badge or claim indexing until the detail page is
confirmed at use time.

## GitHub source search

GitHub code search requires authentication. Prefer the dedicated `gh search`
subcommand which supports structured qualifiers:

```bash
gh search code '<query>' filename:SKILL.md path:skills/ --limit 10
```

The `path:skills/` qualifier filters out SKILL.md files used as project
documentation (not agent skills). If the authenticated CLI is available, this is
the preferred path — one call, scoped results, no dedup needed on the client
side.

When `gh` is installed but not authenticated, try a curl-based web search that
needs no token. GitHub serves a browsable HTML page for code search queries:

```bash
curl -sSfL \
  'https://github.com/search?q=<url-encoded-query>+filename%3ASKILL.md+path%3Askills%2F&type=code'
```

Extract result URLs from the HTML response. Signal that authentication was
missing; a degraded path with HTML scraping is slower and more fragile than the
authenticated API.

When `curl` is also unavailable, fall back to a general web search using
`site:github.com <query> SKILL.md skills/`. Report the missing authenticated and
curl stages.

Verify the current contract in the
[GitHub REST search documentation](https://docs.github.com/en/rest/search/search#search-code).

## Other marketplaces

Treat every third-party marketplace as volatile:

1. open its current documentation or help output;
2. verify authentication, rate limits, pagination, and response shape;
3. distinguish a successful HTTP response from a semantically valid result;
4. inspect the source repository rather than trusting marketplace metadata;
5. record the query timestamp and failure mode.

Never infer safety from ranking, featured placement, download totals, or a 200
status code.
