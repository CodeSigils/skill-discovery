# Catalog and source-search contracts

Prefer provider CLIs and documented APIs. Verify this file against provider
documentation when a query depends on exact authentication or response fields.

## Provider selection and fallback

### Remote source versus local cache

The local-first rule applies to installed and project skills. It does not make
an unverified checkout of an external catalog authoritative. For a catalog such
as learn-skills.dev, prefer the provider's documented remote JSON/RSS artifact
or API at query time. If a checkout is used as an offline or performance cache,
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

### learn-skills.dev remote artifacts

Use the documented publisher artifacts at
`https://raw.githubusercontent.com/NeverSight/learn-skills.dev/main/data/`:

```text
version.json
skills_index.json
skills_search_index.json
skills_search_index2.json
skills_search_index3.json
```

Fetch `version.json` first and record its generation metadata. Search the index
and shards for the original query plus aliases, preserving the provider's full
result count separately from the shortlist. These artifacts are retrieval
sources, not evaluation authorities: cached descriptions, install counts, and
missing enrichment do not establish safety or compatibility. Resolve each
serious result to its canonical repository and reviewed commit. If a remote
artifact is unavailable or its schema is unclear, report that limitation and
continue to the next documented source; do not silently substitute an
unverified local mirror.

Do not query every provider for every request. Search applicable local roots
first, then choose the smallest useful set of external sources:

1. learn-skills.dev's documented generated feed or structured data for the first broad relevance indication;
2. skills.sh directly when its installed CLI or authenticated API is available;
3. other documented catalogs or authenticated GitHub search for canonical source discovery;
4. browser or general web search as a final fallback.

Record each provider's timestamp, authentication state, result count, and failure
mode. Run independent lookups in parallel only when the additional coverage is
useful. Every serious result remains an untrusted pointer until its canonical
repository, exact revision, and complete payload are inspected.

Use learn-skills.dev metadata and trending fields to prioritize inspection, not
to certify a candidate. Popularity is a first indication of what may be useful,
never evidence of quality, safety, compatibility, or user satisfaction.

The Learn Skills UI exposes `Installations`, `Installations Trend`, `Newest`,
`Name`, and `Favorites` sorting, and its top-skills view is installation-sorted
by default. Record the observed sort mode for UI searches. Treat a default or
explicit installation sort as a popularity-biased shortlist: inspect several
task-matching candidates and never describe the first result as the best skill.

The learn-skills.dev repository publishes generated JSON/RSS data. Use those
artifacts for broad retrieval when their current schema and freshness metadata
are verified at use time. This project has not verified a stable public search
API contract, so do not scrape the website or rely on an observed undocumented
endpoint. Preserve the provider's total result count separately from the
shortlist returned for inspection.

For agent retrieval, fetch `data/version.json` and the compact
`data/skills_search_index*.json` shards (or `data/skills_index.json`) before
considering the human-facing `/en/skills?q=...` page. Search IDs, titles, and
descriptions in those artifacts, preserve their timestamp and total count, and
use the UI only as a human-browsing fallback. If the provider later documents a
machine API, prefer that contract; do not infer one from frontend requests.

The canonical publisher is
<https://github.com/NeverSight/learn-skills.dev>. Prefer its generated
`data/skills_search_index*.json` shards, which inline extracted English and
translated descriptions, over recursively scanning `data/skills-md/**` text
files. Description text is cached metadata: use it to retrieve candidates, then
inspect the current source repository and exact revision before recommending.

The publisher's README documents raw GitHub and jsDelivr URLs for
`data/skills.json` and `data/feed.xml`. `skills.json` is the complete leaderboard
payload; RSS/feed data is a small top-list subscription and is not a complete
search source. CDN URLs pinned to `@main` are mutable, so record the retrieval
timestamp and `data/version.json` metadata rather than treating a URL as an
immutable revision. The README's “data updated daily” statement is a provider
claim to verify at use time. Ignore unrelated promotional links in catalog
documentation.

These generated artifacts are reasonably agent-friendly retrieval inputs:
`skills_index.json` exposes stable IDs, source repositories, counts,
descriptions, and cached `skillMdPath` values, while `skills.json` preserves
leaderboard data. They are not an evaluation authority. Descriptions and
cached markdown may be absent because enrichment is coverage-biased, paths may
drift, and leaderboard order reflects popularity. Treat every record as a
pointer that still needs canonical revision and path verification.

The crawler's default GitHub enrichment is coverage-biased: its README says it
fetches cached `SKILL.md` files for top-list entries unless a full sync is
requested. A missing `skillMdPath` or description file therefore records a
provider fetch/coverage limitation, not a failed compatibility or safety check.
Keep that status distinct and inspect the canonical repository when the
candidate remains relevant.

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
