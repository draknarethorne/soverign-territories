# Repository Guidelines

This folder contains cross-cutting working agreements and governance
checklists. It does not replace the project entry point, active plans,
domain-specific contracts or Copilot-discoverable customizations.

## Documents

- [Assistant decision policy](ASSISTANT-DECISION-POLICY.md) and its
  [structured matrix](config/assistant-decision-policy.yaml)
- [Archive guide](ARCHIVE-GUIDE.md)
- [Change management](CHANGE-MANAGEMENT.md)
- [Quality gates](QUALITY-GATES.md)
- [Release checklist](RELEASE-CHECKLIST.md)

Structured companion files belong in `config/`. Keep these documents' local
links and the source-of-truth links in [the documentation map](../README.md)
in sync when moving or adding guidelines. Guideline Markdown uses uppercase
kebab-case filenames; structured YAML uses lowercase kebab-case filenames.

Copilot instructions and on-demand skills remain under `.github/`, where the
host discovers them. The [decision-guidance skill](../../.github/skills/decision-guidance/SKILL.md)
routes autonomous project work to the decision policy; it does not grant
additional authority.
