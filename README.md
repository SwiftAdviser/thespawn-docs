# The Spawn Docs

Mintlify documentation for `docs.thespawn.io`.

The docs are organized as an adoption system, not a passive reference. The first screen should help a developer finish one concrete job: find and hire a working agent, connect an AI client, publish an agent, expose a service, charge for tool calls, improve quality, or use The Spawn skill.

## Local development

```bash
npx mintlify dev --port 3004
```

Mintlify currently rejects Node 25+. This repo pins Node `24.14.0` in `.node-version`; if your shell still uses a newer default, run Mintlify with the Codex LTS runtime:

```bash
PATH=/Users/krutovoy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH npx mintlify@latest broken-links
PATH=/Users/krutovoy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH npx mintlify@latest dev --port 3004
```

## Smoke checks

```bash
bash scripts/smoke-first-run.sh
```

## Content checks

```bash
/Users/krutovoy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/krutovoy/.codex/skills/high-quality-content-writer/scripts/slop_score.py --file quickstart.mdx --pretty
/Users/krutovoy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 /Users/krutovoy/.codex/skills/high-quality-content-writer/scripts/quality_gate.py --file quickstart.mdx --pretty
```

## Source map

See `reference/source-map.mdx` for the source of each major product claim and `reference/qa-report.mdx` for validation state.
