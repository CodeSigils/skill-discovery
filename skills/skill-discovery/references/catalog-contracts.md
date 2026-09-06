# Catalog and source-search contracts

Prefer provider CLIs and documented APIs. Verify this file against provider
documentation when a query depends on exact authentication or response fields.

## Provider selection and fallback

Do not query every provider for every request. Search applicable local roots
first, then choose the smallest useful set of external sources:

1. skills.sh directly when its installed CLI or authenticated API is available;
2. learn-skills.dev's documented structured feed/API for broad retrieval;
3. authenticated GitHub search for canonical source discovery;
4. browser or general web search as a final fallback.

Record each provider's timestamp, authentication state, result count, and failure
mode. Run independent lookups in parallel only when the additional coverage is
useful. Every serious result remains an untrusted pointer until its canonical
repository, exact revision, and complete payload are inspected.

The learn-skills.dev repository publishes generated JSON/RSS data, but this
project has not adopted an undocumented endpoint as a stable API contract. Use a
feed or API only when its current schema, freshness metadata, and access limits
are documented and verified at use time.

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
