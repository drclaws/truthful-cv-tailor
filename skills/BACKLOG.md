# Skills backlog

The **deferred-work ledger**: planned but NOT yet built extensions of this repository — workflows,
tools, roles, and harness adapters. It exists so that a decision already taken ("we will need a
scouting flow, and it will consume the requirements-profile contract") is written down once, instead
of being rediscovered or silently reinvented later.

## Entries have NO authority

This is the hard rule of this file, and it admits no exceptions:

- **An agent must never execute a backlog item as if it existed.** An entry is a note about
  something that has not been built. It is not a specification, not a permission, and not an
  instruction. Referencing an entry as though it were a shipped skill, role, or contract is a
  defect.
- **Nothing here may be cited as a rule or an authority** by a flow, a role, a contract, or an
  artifact. If a step needs a rule, that rule must live in an authoritative file
  (`contracts/*.md`, `roles/<role>/`, `skills/**/SKILL.md`) — the same promotion rule that run
  isolation imposes on run outputs.
- **Promotion happens only when the user asks for the item to be built.** At that point the item
  becomes a real skill or role in its own directory, with its contracts and dependencies declared,
  and its entry is **removed from this file**. An item is either here or built — never both.
- A backlog entry is therefore also the correct answer to "can you run X?" when X only appears
  here: X does not exist yet; say so and offer to build it.

## Entry format

One entry per item, as a level-3 heading, with these fixed fields in this order. Fields are never
omitted; when a field has no content, write `None.` or `To be defined.` rather than dropping it.

```markdown
### <name>

- **Kind:** workflow | tool | role | adapter
- **Intent:** one paragraph — what it does, for whom, and why it is worth building. Enough for a
  reader to judge whether it is still wanted; not enough to be mistaken for a specification.
- **Contracts produced:** contract names this item would write, or `None.`
- **Contracts consumed:** contract names this item would read, or `None.`
- **Dependencies / notes:** what it needs before it can be built — other backlog items, abstract
  capabilities, external data, open questions. Concrete tool names are allowed here only as
  examples of a capability, never as a binding.
```

Entries are grouped by kind, and ordered within a group by name. Naming follows the same convention
as shipped skills (`<verb>-<object>`, lowercase, hyphenated).

## Entries

<!-- Populated when the deferred work items are recorded. Until then, this section is intentionally
     empty: an absent entry means the item was never planned, not that it may be improvised. -->

_None recorded yet._
