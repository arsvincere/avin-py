Для тебя

README отвечает на вопросы:

Что это за папка?
Что здесь лежит?
Что актуально?
Куда добавлять новые инструкции?
Что не надо сюда складывать?

То есть это карта папки.

Для ChatGPT

README отвечает на вопросы:

Какие файлы читать первыми?
Что считать active/current?
Что является архивом?
Какая иерархия source of truth?
Как использовать эти документы в ответах?

То есть это routing-инструкция.

Что должно быть в gpt/README.md

Минимально:

# gpt/

This folder contains ChatGPT configuration, prompts, handoffs, and AI workflow documents for AVIN.

It is not application code.
It is the AI-operations layer of the project.

## Purpose

Use this folder to store:
- current ChatGPT instructions;
- prompt templates;
- AVIN role/mode definitions;
- important handoffs;
- project decision records;
- AI workflow notes;
- context that is important for working with AVIN but does not belong to the codebase.

## Source of truth

When using this folder, priority is:

1. current repository / uploaded archive
2. current user request
3. gpt/current/
4. gpt/decisions/
5. gpt/handoffs/
6. gpt/context/
7. older chats / memory

## Directory structure

- current/
  Active instructions currently used in ChatGPT.

- prompts/
  Reusable prompt templates.

- context/
  Stable background context about AVIN and ChatGPT usage.

- handoffs/
  Important summaries from previous chats.

- decisions/
  Decision records: what was decided, why, and what was postponed.

- archive/
  Old or deprecated versions.

## Rules

- Files in current/ are active.
- Files in archive/ are not active unless explicitly requested.
- If documents conflict, prefer newer ACTIVE documents.
- Do not treat handoffs as stronger than current repo/archive.
- Do not treat old discussions as stronger than current project state.

## How to use with ChatGPT

Example:

Read gpt/README.md and gpt/current/*.
Then answer my question using the current repo/archive as source of truth.

## Important

This folder helps configure ChatGPT behavior.
It does not replace User Instructions or Project Instructions.
It is additional context that must be explicitly provided or referenced.
Моя рекомендация

README должен быть коротким. Не надо туда класть сами инструкции.

Правильная роль README:

README = карта и правила навигации
current/* = активные инструкции
prompts/* = шаблоны
decisions/* = решения
handoffs/* = сжатый контекст
archive/* = старое

То есть README не должен быть “ещё одним огромным handoff”. Он должен помогать быстро понять, что читать и в каком порядке.
