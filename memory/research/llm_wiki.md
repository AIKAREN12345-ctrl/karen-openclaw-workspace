# LLM Wiki Research Findings

## What is it
LLM Wiki is a pattern for building personal knowledge bases using LLMs, introduced by Andrej Karpathy (OpenAI co-founder) in April 2026. Instead of traditional RAG (Retrieval-Augmented Generation) where the LLM rediscovers knowledge from scratch on every query, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and your raw sources.

## Key Features
- **Three-layer architecture**: (1) Raw sources (immutable documents), (2) The wiki (LLM-generated markdown files with summaries, entity pages, concept pages), and (3) The schema (configuration file like CLAUDE.md or AGENTS.md that guides the LLM)
- **Core operations**: Ingest (process new sources into the wiki), Query (ask questions against compiled knowledge), and Lint (health-check for contradictions, stale claims, orphan pages)
- **Compounding knowledge**: Cross-references are pre-built, contradictions are flagged during ingestion, and synthesis reflects everything you've read — the wiki gets richer with every source and question
- **Tooling ecosystem**: Obsidian as the IDE/viewer, Obsidian Web Clipper for ingestion, qmd for local search, Marp for slide decks, Dataview for frontmatter queries, and Git for version control

## Significance for 2026
- Represents a shift from "vibe coding" to "knowledge compilation" — Karpathy noted he's spending more tokens on manipulating knowledge than code
- Introduces the "idea file" concept: sharing structured patterns rather than specific code/apps, letting each person's LLM agent customize the implementation
- Solves the maintenance problem that killed human-managed wikis — LLMs don't get bored, don't forget cross-references, and can touch 15 files in one pass
- Realizes Vannevar Bush's 1945 Memex vision: a personal, curated knowledge store with associative trails, where the LLM finally handles the maintenance burden humans couldn't sustain
