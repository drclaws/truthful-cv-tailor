#!/usr/bin/env python3
"""Scaffold one run of the generate-targeted-cv workflow and seed its run.md.

The rules of the flow live in the SKILL.md next to this script; the script only
creates the layout that file declares and writes the manifest seed. Every value
is an explicit command-line argument resolved by the calling agent: nothing is
derived from repository layout, and no context, rules or contract file is ever
read here. In particular, the candidate's identity and the export filename are
passed in — this script does not know the export naming rule and must not guess
it.

What it creates, under the run directory the caller passes:

    <run>/run.md        the run-manifest seed (status: in-progress)
    <run>/position/     the job dossier: stubs on a first run, a copy of the
                        previous run's dossier on a rerun (--copy-position)
    <run>/render/       intermediate: typeset source and build byproducts
    <run>/exports/      intermediate: the deliverable
    <run>/work/         intermediate: check byproducts and prepared inputs
    <run>/checks/       only when an internal validator is registered
    <run>/external/     only when an external validator is registered

Nothing that already exists is overwritten unless --force is passed, and a run
directory that already holds a run is refused: a rerun gets its own run id.

Exit codes: 0 success (warnings are printed, not fatal), 1 nothing was created
(refused or unwritable), 2 a usage error in the arguments.

    create_run.py --run-dir outputs/generate-targeted-cv/<run-id> \
        --run-id <run-id> --bank-dir outputs/knowledge-bank \
        --export-name <FirstNameSurname>.pdf \
        --validator "<name>:internal" --step "Resolve user context|flow"
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

FLOW_NAME = "generate-targeted-cv"
FLOW_VERSION = "1.0"
CONTRACT_VERSION = "1.0"

# The dossier files the job-dossier contract names. Seeded as stubs on a first
# run so the user knows what to fill; a file with nothing to say is deleted
# rather than filled with speculation.
POSITION_STUBS = {
    "job_description.md": (
        "# Job description\n\n"
        "Paste the vacancy text here, as close to verbatim as the source allows.\n"
    ),
    "recruiter_notes.md": (
        "# Recruiter notes\n\n"
        "Screening signals and recruiter or hiring-manager statements. Point at the\n"
        "transcript they were drawn from when one exists. Delete this file if the run\n"
        "has no people-side input.\n"
    ),
    "company_notes.md": (
        "# Company notes\n\n"
        "What the company does, its stage and market, team structure — anything that\n"
        "shapes positioning. Delete this file if there is nothing to record.\n"
    ),
}

STEP_COLUMNS = ("step", "executor", "contract", "artifact", "group")
GATE_COLUMNS = ("gate", "requires", "evidenced by")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="create_run.py",
        description=(
            "Scaffold a generate-targeted-cv run directory and seed its run.md. "
            "All values are passed explicitly; nothing is read from context or "
            "rules files."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Repeatable arguments that fill a table (--step, --gate) take "
            "pipe-separated fields; missing trailing fields become em dashes.\n"
            "  --step 'Write the draft|experience-writer.write-document|"
            "cv-document|draft_cv.md|-'\n"
            "  --gate 'G5 truthfulness|the mandatory fact-check passed|fact_check.md'"
        ),
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="the run directory to create, computed by the flow (it is never derived here)",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="the run identifier recorded in the manifest envelope (the vacancy slug)",
    )
    parser.add_argument(
        "--flow-name", default=FLOW_NAME, help="flow name recorded in the manifest"
    )
    parser.add_argument(
        "--flow-version",
        default=FLOW_VERSION,
        help="flow version recorded in the manifest (default: %(default)s)",
    )
    parser.add_argument(
        "--contract-version",
        default=CONTRACT_VERSION,
        help=(
            "the run-manifest contract version this seed is written against, read "
            "from the contract by the caller (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--date",
        default=None,
        help="ISO-8601 date or date+time for the envelope (default: today, from the environment)",
    )
    parser.add_argument(
        "--bank-dir", default=None, help="the knowledge bank directory, recorded as an input"
    )
    parser.add_argument(
        "--constraints-ledger",
        default=None,
        help="the constraints ledger path, recorded as an input",
    )
    parser.add_argument(
        "--candidate-name",
        default=None,
        help=(
            "the candidate's full name as the bank's ## Candidate section records it, "
            "resolved by the flow; recorded, never parsed and never used to build a filename"
        ),
    )
    parser.add_argument(
        "--export-name",
        default=None,
        help=(
            "the deliverable filename the flow's export naming rule produced; recorded "
            "as-is (this script does not know the rule)"
        ),
    )
    parser.add_argument(
        "--copy-position",
        default=None,
        help="a previous run's position/ directory to copy into this run (rerun dossier copy)",
    )
    parser.add_argument(
        "--no-position-stubs",
        action="store_true",
        help="create position/ empty instead of seeding the job-dossier stub files",
    )
    parser.add_argument(
        "--context-resolution",
        action="append",
        default=[],
        metavar="TEXT",
        help="repeatable: which mechanism supplied which user-context values",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="TEXT",
        help="repeatable: a resolved canonical experience source, recorded in the snapshot",
    )
    parser.add_argument(
        "--validator",
        action="append",
        default=[],
        metavar="NAME:KIND",
        help=(
            "repeatable: a registered validation-set entry as name:kind, kind being "
            "internal or external; checks/ and external/ are created accordingly"
        ),
    )
    parser.add_argument(
        "--setting",
        action="append",
        default=[],
        metavar="TEXT",
        help="repeatable: a per-skill setting in force, recorded verbatim in the snapshot",
    )
    parser.add_argument(
        "--additional-rule",
        action="append",
        default=[],
        metavar="TEXT",
        help="repeatable: an additional rule from user context the run must honour",
    )
    parser.add_argument(
        "--bank-freshness",
        action="append",
        default=[],
        metavar="TEXT",
        help="repeatable: the freshness verdict and per-source statuses, as the check returned them",
    )
    parser.add_argument(
        "--step",
        action="append",
        default=[],
        metavar="ROW",
        help="repeatable, in execution order: a step checklist row, fields separated by |",
    )
    parser.add_argument(
        "--gate",
        action="append",
        default=[],
        metavar="ROW",
        help="repeatable: a gate row, fields separated by |",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="write into an existing run directory and reseed run.md (never the dossier)",
    )
    parser.add_argument("--json", action="store_true", help="print a machine-readable summary")
    return parser.parse_args(argv)


def split_row(raw, columns):
    """Split a pipe-separated row into exactly len(columns) cells."""
    cells = [cell.strip() for cell in raw.split("|")]
    cells = [cell if cell else "—" for cell in cells]
    if len(cells) < len(columns):
        cells += ["—"] * (len(columns) - len(cells))
    return cells[: len(columns)]


def parse_validators(entries, warnings):
    """Return [(name, kind)] for well-formed entries; warn about the rest."""
    parsed = []
    for entry in entries:
        name, separator, kind = entry.rpartition(":")
        name, kind = name.strip(), kind.strip().lower()
        if not separator or not name or kind not in ("internal", "external"):
            warnings.append(
                f"validation-set entry {entry!r} is not '<name>:internal' or "
                "'<name>:external'; recorded as unclassified, and no directory was "
                "created for it"
            )
            parsed.append((entry.strip(), "unclassified"))
            continue
        parsed.append((name, kind))
    return parsed


def bullet_list(values, empty):
    if not values:
        return f"{empty}\n"
    return "".join(f"- {value}\n" for value in values)


def table(columns, rows, empty_note):
    header = "| " + " | ".join(columns) + " |\n"
    header += "|" + "|".join("---" for _ in columns) + "|\n"
    if not rows:
        return header + f"\n{empty_note}\n"
    return header + "".join("| " + " | ".join(row) + " |\n" for row in rows)


def build_manifest(args, validators, step_rows, gate_rows, stamp):
    inputs = ["position/ — job-dossier"]
    if args.bank_dir:
        inputs.append(f"{args.bank_dir} — knowledge-bank")
    if args.constraints_ledger:
        inputs.append(f"{args.constraints_ledger} — constraints-ledger")

    envelope = [
        "---",
        "contract: run-manifest",
        f"contract_version: {args.contract_version}",
        f"producer: flow:{args.flow_name}",
        f"run_id: {args.run_id}",
        "status: in-progress",
        "revision: 1",
        f"created: {stamp}",
        f"updated: {stamp}",
        "inputs:",
    ]
    envelope += [f"  - {item}" for item in inputs]
    envelope.append("---")

    validation_lines = [f"{name} ({kind})" for name, kind in validators]
    step_table = table(
        ("step", "executor", "contract", "artifact", "group", "status", "revision", "notes"),
        step_rows,
        "_No steps were passed to the scaffolder; the flow fills one row per step of its step table._",
    )
    gate_table = table(
        ("gate", "requires", "state", "evidenced by"),
        gate_rows,
        "_No gates were passed to the scaffolder; the flow fills one row per gate it declares._",
    )

    body = f"""

# Run manifest — {args.run_id}

Seeded by `scripts/create_run.py`. **Written as the run proceeds**, never reconstructed at the end:
a later step, a resuming agent and the user all read the state of the run from this file.

## Run

| Field | Value |
|---|---|
| run id | {args.run_id} |
| flow | {args.flow_name} |
| flow version | {args.flow_version} |
| started | {stamp} |
| ended | — |

## Inputs

{bullet_list(inputs, "None recorded.")}
## User context

**Resolution used**

{bullet_list(args.context_resolution, "To be recorded by the flow at preflight.")}
**Resolved snapshot — canonical experience sources**

{bullet_list(args.source, "To be recorded by the flow at preflight.")}
**Resolved snapshot — active validation set**

{bullet_list(validation_lines, "Empty set recorded. The mandatory truthfulness check runs regardless.")}
**Resolved snapshot — per-skill settings in force**

{bullet_list(args.setting, "None recorded.")}
**Resolved snapshot — additional rules**

{bullet_list(args.additional_rule, "None recorded.")}
**Candidate identity and export name**

| Field | Value |
|---|---|
| candidate (from the bank's `## Candidate` section) | {args.candidate_name or "to be resolved"} |
| export name (from the flow's naming rule) | {args.export_name or "to be resolved"} |

## Bank freshness

{bullet_list(args.bank_freshness, "To be recorded by the flow from the freshness check.")}
## Steps

{step_table}
## Gates

{gate_table}
## Artifact index

| path | contract | status | revision |
|---|---|---|---|
| run.md | run-manifest | in-progress | 1 |
| position/ | job-dossier | in-progress | 1 |
| render/ | — (intermediate: typeset source and build byproducts) | — | — |
| exports/ | — (intermediate: the deliverable) | — | — |
| work/ | — (byproducts: prepared check inputs, raw script captures) | — | — |

## Open questions

_None yet._
"""
    return "\n".join(envelope) + body


def scaffold_directories(run_dir, kinds, created):
    directories = [
        run_dir,
        run_dir / "position",
        run_dir / "render",
        run_dir / "exports",
        run_dir / "work",
    ]
    if "internal" in kinds:
        directories.append(run_dir / "checks")
    if "external" in kinds:
        directories.append(run_dir / "external")

    for directory in directories:
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if not existed:
            created.append(str(directory))


def copy_dossier(source_arg, position, created, warnings):
    source = Path(source_arg)
    if not source.is_dir():
        warnings.append(
            f"--copy-position {source} is not a readable directory; the dossier was not "
            "copied. Copy it by hand, or seed the stubs instead."
        )
        return
    for item in sorted(source.rglob("*")):
        target = position / item.relative_to(source)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            warnings.append(f"{target} already exists; left untouched")
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
        except OSError as exc:
            warnings.append(f"could not copy {item}: {exc}")
            continue
        created.append(str(target))


def seed_stubs(position, created, warnings):
    for name, content in POSITION_STUBS.items():
        target = position / name
        if target.exists():
            continue
        try:
            target.write_text(content, encoding="utf-8")
        except OSError as exc:
            warnings.append(f"could not write {target}: {exc}")
            continue
        created.append(str(target))


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    warnings = []
    created = []

    run_dir = Path(args.run_dir)
    if run_dir.exists() and any(run_dir.iterdir()) and not args.force:
        print(
            f"refusing to scaffold into {run_dir}: it exists and is not empty.\n"
            "A rerun gets its own run id (append -2, -3, …) so that no run is ever "
            "overwritten; pass --force only to finish scaffolding a run you started.",
            file=sys.stderr,
        )
        return 1

    validators = parse_validators(args.validator, warnings)
    kinds = {kind for _, kind in validators}

    try:
        scaffold_directories(run_dir, kinds, created)
    except OSError as exc:
        print(f"cannot create the run layout under {run_dir}: {exc}", file=sys.stderr)
        return 1

    position = run_dir / "position"
    if args.copy_position:
        copy_dossier(args.copy_position, position, created, warnings)
    elif not args.no_position_stubs:
        seed_stubs(position, created, warnings)

    stamp = args.date or date.today().isoformat()
    step_rows = [split_row(raw, STEP_COLUMNS) + ["pending", "—", "—"] for raw in args.step]
    gate_rows = [
        [cells[0], cells[1], "not reached", cells[2]]
        for cells in (split_row(raw, GATE_COLUMNS) for raw in args.gate)
    ]

    manifest = run_dir / "run.md"
    if manifest.exists() and not args.force:
        warnings.append(f"{manifest} already exists; left untouched (pass --force to reseed it)")
    else:
        try:
            manifest.write_text(
                build_manifest(args, validators, step_rows, gate_rows, stamp), encoding="utf-8"
            )
        except OSError as exc:
            print(f"cannot write {manifest}: {exc}", file=sys.stderr)
            return 1
        created.append(str(manifest))

    if args.json:
        print(
            json.dumps(
                {
                    "run_dir": str(run_dir),
                    "run_id": args.run_id,
                    "created": created,
                    "warnings": warnings,
                },
                indent=2,
            )
        )
        return 0

    print(f"scaffolded run {args.run_id} at {run_dir}")
    for item in created:
        print(f"  created {item}")
    for warning in warnings:
        print(f"  warning: {warning}")
    if not args.step:
        print("  note: no --step rows were passed; fill ## Steps from the flow's step table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
