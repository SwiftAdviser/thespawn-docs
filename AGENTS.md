# The Spawn Docs Agent Guide

This repository is a Mintlify documentation site for `docs.thespawn.io`.

The docs are an adoption system. Start from the developer job, prove a working first-run journey, then expand reference material around that path.

## Source Repositories

- Product app: `/Users/krutovoy/Projects/agentspawn`
- spawnr CLI: `/Users/krutovoy/Projects/thespawn-cli`
- Historical docs workflow: `/Users/krutovoy/Projects/mandate-docs`
- Historical product source: `/Users/krutovoy/Projects/mandate`

## Working Rules

- Do not invent product behavior. Cite code, live endpoint behavior, or existing docs in `reference/source-map.mdx`.
- Prefer verified commands over prose. If a command was not run, label it as unverified and say why.
- Use customer jobs as top-level organization: find and hire an agent, connect an AI client, publish an agent, expose a service, charge for a tool call, improve quality, use the thespawn skill.
- Hide protocol complexity until it helps the user complete the job. Explain ERC-8004, MCP, x402, and onchain identity after the first useful action.
- Every path page needs a success checkpoint, a failure branch, and a community fallback.
- Use `high-quality-content-writer` gates before considering a page ready.

## Local Checks

```bash
npx mintlify dev --port 3004
bash scripts/smoke-first-run.sh
```

For content quality, run:

```bash
/Users/krutovoy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/krutovoy/.codex/skills/high-quality-content-writer/scripts/slop_score.py --file <page>.mdx --pretty
/Users/krutovoy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/krutovoy/.codex/skills/high-quality-content-writer/scripts/quality_gate.py --file <page>.mdx --pretty
```
