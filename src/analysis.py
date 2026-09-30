"""Load the per-artifact evaluation records and compute the paper's metrics.

Each row of data/results/{agent}_{language}_reproducibility_analysis.csv is one
generated artifact (100 prompts x 3 agents = 300 rows). The columns used here:

  execution_success  true / false / partial (case varies; partial counts as failure)
  error_type         label assigned by the failure-classification protocol (Algorithm 1)
  claimed_count      |D_c|, packages declared in the agent's manifest
  runtime_count      |D_r|, packages observed at runtime (Sciunit / npm list / mvn dependency:tree)
  completeness_gap   |D_m|, declared-but-missing direct imports
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

AGENTS = ["claude", "codex", "gemini"]
LANGUAGES = ["python", "javascript", "java"]
AGENT_NAME = {"claude": "Claude", "codex": "Codex", "gemini": "Gemini"}
LANG_NAME = {"python": "Python", "javascript": "JavaScript", "java": "Java"}

# Raw error_type labels in the CSVs -> the paper's error categories (Table 5).
# Failures without an error_type label are assigned to "Other".
ERROR_TAXONOMY = {
    "CodeBug": "Syntax Errors",
    "CodeBug-Fixed": "Syntax Errors",
    "CodeBug-Unfixable": "Syntax Errors",
    "NotProcessed": "Malformed Output",
    "ConfigError-Partial": "Configuration",
    "MissingData": "System Error",
    "BuildRequired": "System Error",
    "RuntimeEnvRequired": "System Error",
    "ImportError": "Dependency",
    "DependencyMissing": "Dependency",
    "CompletenessGap-Fixed": "Dependency",
    "CompletenessGap-Unfixable": "Dependency",
    "KeyError": "Other",
    "MissingCredentials": "Other",
}
CODE_ERRORS = ["Syntax Errors", "Malformed Output"]
ENV_ERRORS = ["Configuration", "Other", "System Error", "Dependency"]


def load(results_dir: Path) -> pd.DataFrame:
    frames = [pd.read_csv(f) for f in sorted(Path(results_dir).glob("*_reproducibility_analysis.csv"))]
    if not frames:
        raise FileNotFoundError(f"no result CSVs in {results_dir}")
    df = pd.concat(frames, ignore_index=True)
    df["agent"] = df["llm_name"].str.strip().str.lower()
    df["lang"] = df["language"].str.strip().str.lower()
    status = df["execution_success"].astype(str).str.strip().str.lower()
    df["outcome"] = status.map({"true": "success", "partial": "partial"}).fillna("failed")
    df["success"] = df["outcome"] == "success"
    df["claimed"] = pd.to_numeric(df["claimed_count"], errors="coerce").fillna(0).astype(int)
    df["runtime"] = pd.to_numeric(df["runtime_count"], errors="coerce").fillna(0).astype(int)
    df["gap"] = pd.to_numeric(df["completeness_gap"], errors="coerce").fillna(0).astype(int)
    # An artifact has a completeness gap if a missing direct import was recorded,
    # either in completeness_gap or through a CompletenessGap-* error label.
    df["has_gap"] = (df["gap"] > 0) | df["error_type"].astype(str).str.contains("CompletenessGap")
    df["error_category"] = df["error_type"].map(ERROR_TAXONOMY)
    df.loc[~df["success"] & df["error_category"].isna(), "error_category"] = "Other"
    return df


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score interval for k successes out of n, in percent."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (100 * (centre - half), 100 * (centre + half))


def by_agent(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, sub in [(AGENT_NAME[a], df[df.agent == a]) for a in AGENTS] + [("Overall", df)]:
        n, s = len(sub), int(sub.success.sum())
        rows.append({"agent": key, "total": n, "success": s, "failed": n - s,
                     "partial": int((sub.outcome == "partial").sum()), "rate": round(100 * s / n, 1)})
    return pd.DataFrame(rows)


def by_language(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for lang in LANGUAGES:
        sub = df[df.lang == lang]
        n, s = len(sub), int(sub.success.sum())
        lo, hi = wilson(s, n)
        rows.append({"language": LANG_NAME[lang], "total": n, "success": s, "rate": round(100 * s / n, 1),
                     "ci_low": round(lo, 1), "ci_high": round(hi, 1)})
    return pd.DataFrame(rows)


def by_agent_language(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for a in AGENTS:
        for lang in LANGUAGES:
            sub = df[(df.agent == a) & (df.lang == lang)]
            n, s = len(sub), int(sub.success.sum())
            lo, hi = wilson(s, n)
            rows.append({"agent": AGENT_NAME[a], "language": LANG_NAME[lang], "n": n, "success": s,
                         "rate": round(100 * s / n, 1), "ci_low": round(lo, 1), "ci_high": round(hi, 1),
                         "with_gap": int(sub.has_gap.sum())})
    return pd.DataFrame(rows)


def error_table(df: pd.DataFrame) -> pd.DataFrame:
    fails = df[~df.success]
    counts = fails.error_category.value_counts()
    total = len(fails)
    rows = []
    for group, cats in [("Code Errors", CODE_ERRORS), ("Environment", ENV_ERRORS)]:
        for c in cats:
            rows.append({"group": group, "category": c, "count": int(counts.get(c, 0)),
                         "pct": round(100 * counts.get(c, 0) / total, 1)})
        sub = int(sum(counts.get(c, 0) for c in cats))
        rows.append({"group": group, "category": "Subtotal", "count": sub, "pct": round(100 * sub / total, 1)})
    rows.append({"group": "Total", "category": "", "count": total, "pct": 100.0})
    return pd.DataFrame(rows)


def errors_by_agent(df: pd.DataFrame) -> pd.DataFrame:
    fails = df[~df.success]
    tab = pd.crosstab(fails.error_category, fails.agent).reindex(CODE_ERRORS + ENV_ERRORS, fill_value=0)
    tab = tab.reindex(columns=AGENTS, fill_value=0)
    tab.loc["CODE"] = tab.loc[CODE_ERRORS].sum()
    tab.loc["ENV"] = tab.loc[ENV_ERRORS].sum()
    tab.columns = [AGENT_NAME[a] for a in tab.columns]
    return tab


def runtime_expansion(df: pd.DataFrame) -> pd.DataFrame:
    """Claimed vs runtime dependencies per language.

    The multiplier is the ratio of the mean runtime count to the mean claimed
    count (Section 2.1), over artifacts with at least one claimed dependency.
    The overall figure weights each language's multiplier by its number of
    artifacts (120 / 105 / 75).
    """
    rows = []
    for lang in LANGUAGES:
        sub = df[(df.lang == lang) & (df.claimed > 0)]
        c, r = sub.claimed.mean(), sub.runtime.mean()
        rows.append({"language": LANG_NAME[lang], "n": len(sub), "claimed": round(c, 1),
                     "runtime": round(r, 1), "multiplier": round(r / c, 1), "_exact": r / c,
                     "_weight": int((df.lang == lang).sum())})
    out = pd.DataFrame(rows)
    weighted = (out._exact * out._weight).sum() / out._weight.sum()
    out = out.drop(columns=["_exact", "_weight"])
    out.attrs["weighted_multiplier"] = weighted
    return out
