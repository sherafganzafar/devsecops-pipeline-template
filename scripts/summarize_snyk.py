#!/usr/bin/env python3
"""Summarize a Snyk JSON report and fail the build on serious findings.

Usage: summarize_snyk.py snyk-results.json [--fail-on high]
Writes a Markdown table to $GITHUB_STEP_SUMMARY when running in GitHub Actions.
"""
import argparse
import json
import os
import sys

ORDER = ["low", "medium", "high", "critical"]


def load_vulns(path):
    with open(path) as f:
        data = json.load(f)
    reports = data if isinstance(data, list) else [data]
    vulns = []
    for r in reports:
        vulns.extend(r.get("vulnerabilities", []))
    return vulns


def main():
    p = argparse.ArgumentParser()
    p.add_argument("report")
    p.add_argument("--fail-on", choices=ORDER, default="high")
    args = p.parse_args()

    vulns = load_vulns(args.report)
    counts = {s: 0 for s in ORDER}
    for v in vulns:
        sev = v.get("severity", "low")
        counts[sev] = counts.get(sev, 0) + 1

    lines = ["## Snyk scan summary", "", "| Severity | Count |", "|---|---|"]
    for s in reversed(ORDER):
        lines.append(f"| {s} | {counts[s]} |")
    top = [v for v in vulns if v.get("severity") in ("high", "critical")][:10]
    if top:
        lines += ["", "### Top findings", ""]
        for v in top:
            fix = ", ".join(v.get("fixedIn", [])) or "no fix yet"
            lines.append(
                f"- **{v.get('severity')}** {v.get('packageName')}@{v.get('version')}: "
                f"{v.get('title')} (fixed in: {fix})"
            )
    text = "\n".join(lines)
    print(text)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(text + "\n")

    threshold = ORDER.index(args.fail_on)
    blocked = sum(counts[s] for s in ORDER[threshold:])
    if blocked:
        print(f"\nFAIL: {blocked} finding(s) at '{args.fail_on}' or above.")
        return 1
    print("\nPASS: nothing at or above the threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
