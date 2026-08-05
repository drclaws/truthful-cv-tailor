# Capability: knowledge-bank-curator.check-freshness

## Purpose

Decide whether the knowledge bank still reflects the candidate's canonical sources, and say so in a
form a flow can act on: one verdict plus a per-source status. Flows call this at preflight; a stale
verdict sends them to the bank refresh flow before any evidence is retrieved. This capability reads
only — it never rebuilds anything.

## Inputs

| Input | Contract / description | Required |
|---|---|---|
| `sources` | The resolved canonical experience sources — paths, URLs, or descriptions. The caller resolved them from user context; this capability does not resolve anything itself. | required |
| `bank_dir` | The knowledge bank directory. | required |
| `index_paths` | The bank index files to check, if the caller wants a subset. Default: every index the `knowledge-bank` contract declares. | optional |

## Outputs

Returned to the caller, not written to disk (the flow records it in its run report, and the analyst
carries it into the bank stanza of the `source-audit`):

| Field | Values |
|---|---|
| `verdict` | `fresh` — every index is current; `stale` — at least one index is missing, older than a source, or has no source-metadata block; `unknown` — no index problem, but a source could not be read, so freshness cannot be decided. |
| `per_source` | One line per source: `ok` / `missing` / `unreadable` / `not-time-checkable`, with the timestamp where one exists and the reason where it does not. |
| `per_index` | One line per index: status, timestamp, whether the source-metadata block is present. |
| `next_action` | What the flow should do: proceed, refresh (full or which sections), or resolve the source problem first. |

## Procedure

1. **Split the sources.** Sources that resolve to a file or a directory are *time-checkable*.
   Sources that are URLs, dictated content, or plain descriptions are **not** time-checkable by
   timestamp — handle them in step 4.
2. **Run the freshness script** with the time-checkable sources and the index paths as explicit
   arguments. The script is `scripts/check_sources_freshness.py`, next to this role card; it takes
   every path on the command line and reads no context or rule files.

   ```
   check_sources_freshness.py \
       --source <source-path> [--source <source-path> …] \
       --index <bank-dir>/<index-file> [--index <bank-dir>/<index-file> …] \
       [--format json]
   ```

   Exit codes: `0` fresh, `1` refresh-required, `3` unknown (a source is missing or unreadable),
   `2` a usage error in the arguments you passed.
3. **Resolve every `unreadable` source before trusting the verdict.** `unreadable` means the path
   exists but yielded no content — a permissions boundary the shell cannot cross, or a placeholder
   stub left on disk by cloud-synced storage whose real content has been evicted. The script reports
   it and stops there by design; the fallback is defined here:
   1. re-read the source through the harness's own file tools, which may have access the shell lacks;
   2. if that works, treat the source as `ok` and use the timestamp the script reported;
   3. if it does not, **ask the user** to make the source available (fetch the content, grant access,
      or replace the entry with a reachable one). Never quietly drop it — a source dropped from the
      comparison makes a stale bank look fresh.
4. **Judge the sources that carry no timestamp** by their record in the bank's source-metadata
   block: if a source is listed there with the date it was last confirmed, and the user has not said
   it changed, report it as `not-time-checkable` with that date and treat it as current. If it is
   absent from the block, the bank has never seen it — that alone makes the verdict `stale`.
5. **Compose the verdict.** Any missing, stale, or metadata-less index ⇒ `stale`. Otherwise, any
   unresolved source problem ⇒ `unknown`. Otherwise `fresh`.
6. **Recommend the next action**, at the granularity the evidence supports: a single changed source
   can justify a partial refresh naming the affected sections; anything broader is a full rebuild.

## Rules

- **Read-only.** This capability never writes the bank, the ledger, or any artifact. Its output is a
  verdict handed back to the caller.
- **Content, not just timestamps.** A modification time proves nothing about a file whose content has
  been evicted; that is why the script probes for readable bytes and why `unreadable` is a status
  rather than a crash.
- **A missing source-metadata block means stale**, whatever the timestamps say: an index that cannot
  state what it was built from cannot be shown to be current.
- **`unknown` is a legitimate verdict** and must be reported as such. Do not round it to `fresh`
  because most sources were fine, and do not round it to `stale` to be safe — the flow decides, and
  it needs to know which situation it is in.
- **An index newer than every source is not proof of correctness**, only of recency. Coverage and
  accuracy are the build's gates, not this one's.
- The script is passed values the caller resolved. If a source path is empty, malformed, or clearly a
  description rather than a path, do not pass it to the script — classify it in step 1 instead.

## Failure and skip conditions

- **The bank directory or every index is missing** — verdict `stale`, next action: full build. This
  is a normal first-run outcome, not an error.
- **A source is missing** (the path does not exist) — report it per source and ask the user whether
  it moved or should be removed from their context; verdict stays `unknown` unless an index problem
  already forced `stale`.
- **A source stays unreadable after the fallback** — verdict `unknown`, with the source named and the
  reason quoted. The flow decides whether to proceed at its own risk or stop.
- **The script cannot be executed at all** — fall back to comparing timestamps and content presence
  with the harness's own file tools, following exactly the rules above, and note in the output that
  the check was done manually. A missing script runtime never fails a flow.
- **No sources were passed** — report `unknown` with the reason "no canonical sources were
  resolved"; this is a user-context problem for the caller to raise at preflight.
