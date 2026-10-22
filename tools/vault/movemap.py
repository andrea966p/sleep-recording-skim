"""Read the reviewed move map (vault/_meta/move-map.tsv).

Columns: old_path new_path type area status canonical superseded_by banner confidence reason
new_path is a vault-relative path, `DELETE`, or `OUT:<repo-relative path>`.
Files not listed keep their path.
"""
from __future__ import annotations

import csv
import posixpath
from dataclasses import dataclass


@dataclass
class Row:
    old: str
    new: str
    type: str = "-"
    area: str = "-"
    status: str = "-"
    canonical: str = "-"
    superseded_by: str = "-"
    banner: str = "-"
    confidence: str = "-"
    reason: str = "-"

    @property
    def delete(self) -> bool:
        return self.new == "DELETE"

    @property
    def out(self) -> str | None:
        return self.new[4:] if self.new.startswith("OUT:") else None

    @property
    def stays_in_vault(self) -> bool:
        return not self.delete and self.out is None

    @property
    def renamed(self) -> bool:
        return self.stays_in_vault and posixpath.basename(self.new) != posixpath.basename(self.old)


def load(path: str) -> dict[str, Row]:
    rows: dict[str, Row] = {}
    with open(path, encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter="\t")
        header = next(rd)
        assert header[:2] == ["old_path", "new_path"], header
        for rec in rd:
            if not rec or not rec[0].strip():
                continue
            rec = [c.strip() for c in rec] + ["-"] * (10 - len(rec))
            r = Row(*rec[:10])
            if r.old in rows:
                raise SystemExit(f"duplicate old_path in move map: {r.old}")
            rows[r.old] = r
    return rows


def final_path(rows: dict[str, Row], old: str) -> str | None:
    """Where `old` ends up in the vault after the whole migration (None if it leaves)."""
    r = rows.get(old)
    if r is None:
        return old
    return r.new if r.stays_in_vault else None


def renamed_in_place(rows: dict[str, Row], old: str) -> str | None:
    """Old path with only the basename changed (the P3 state), or the old path."""
    r = rows.get(old)
    if r is None or not r.stays_in_vault:
        return old if r is None else None
    return posixpath.join(posixpath.dirname(old), posixpath.basename(r.new))
