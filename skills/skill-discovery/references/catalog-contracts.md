# Catalog and source-search contracts

Prefer provider CLIs and documented APIs. Verify this file against provider
documentation when a query depends on exact authentication or response fields.

## skills.sh

For interactive/local discovery, use the official installer CLI:

```bash
npx --yes skills find '<query>'
npx --yes skills add <owner/repository> --list
```

Programmatic search uses the documented v1 endpoint:

```text
GET https://skills.sh/api/v1/skills/search?q=<query>&limit=<n>
Authorization: Bearer <Vercel OIDC token>
```

The response places results in `data`. Authentication and rate limits are part
of the contract; see <https://www.skills.sh/docs/api>. Do not rely on the legacy
unauthenticated `/api/search` endpoint even if it happens to respond.

## GitHub source search

GitHub code search requires authentication. Prefer an authenticated CLI call:

```bash
gh api --method GET search/code -f q='<query> filename:SKILL.md' -f per_page=10
```

If authentication is unavailable, use GitHub's browser search or a web search
such as `site:github.com <query> SKILL.md`. Report the missing authenticated stage.
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
