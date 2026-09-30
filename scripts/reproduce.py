"""Regenerate the paper's tables and figures from data/results and compare them
with the published values in results/paper_values.json.

    python scripts/reproduce.py            # tables, figures and comparison
    python scripts/reproduce.py --no-figures

Writes results/tables/*.csv, results/figures/*.png and results/comparison.csv.
Values are compared at the precision printed in the paper; confidence-interval
bounds use a tolerance of 0.1. Exits with status 1 if any compared value differs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import analysis as A  # noqa: E402


CI_TOLERANCE = 0.1


def compare(paper: dict, df) -> list[dict]:
    rows = []

    def add(claim, published, reproduced, tol=0.05):
        """Numbers must agree to the precision printed in the paper (one decimal
        unless a different tol is given); labels such as "27 (4)" must be equal."""
        if isinstance(published, list):
            ok = all(abs(a - b) <= tol + 1e-9 for a, b in zip(published, reproduced))
        elif isinstance(published, (int, float)):
            ok = abs(float(published) - float(reproduced)) <= tol + 1e-9
        else:
            ok, tol = published == reproduced, ""
        rows.append({"claim": claim, "paper": published, "reproduced": reproduced,
                     "tolerance": tol, "match": "yes" if ok else "no"})

    t2 = A.by_agent(df).set_index("agent")
    for agent, v in paper["table2_agent"].items():
        r = t2.loc[agent]
        add(f"Table 2 {agent} success", v["success"], int(r.success))
        add(f"Table 2 {agent} failed (partial)", f'{v["failed"]} ({v["partial"]})', f"{int(r.failed)} ({int(r.partial)})")
        add(f"Table 2 {agent} rate %", v["rate"], float(r.rate))

    t3 = A.by_language(df).set_index("language")
    for lang, v in paper["table3_language"].items():
        r = t3.loc[lang]
        add(f"Table 3 {lang} success/total", f'{v["success"]}/{v["total"]}', f"{int(r.success)}/{int(r.total)}")
        add(f"Table 3 {lang} rate %", v["rate"], float(r.rate))
        add(f"Table 3 {lang} 95% CI", v["ci"], [float(r.ci_low), float(r.ci_high)], tol=CI_TOLERANCE)

    t4 = A.by_agent_language(df).set_index(["agent", "language"])
    for key, v in paper["table4_agent_language"].items():
        agent, lang = key.split("|")
        r = t4.loc[(agent, lang)]
        add(f"Table 4 {agent} {lang} success/n", f'{v["success"]}/{v["n"]}', f"{int(r.success)}/{int(r.n)}")
        add(f"Table 4 {agent} {lang} rate %", v["rate"], float(r.rate))
        add(f"Table 4 {agent} {lang} 95% CI", v["ci"], [float(r.ci_low), float(r.ci_high)], tol=CI_TOLERANCE)

    t5 = A.error_table(df)
    cell = lambda g, c, col: t5[(t5.group == g) & (t5.category == c)][col].iloc[0]  # noqa: E731
    rows5 = [(c, "Code Errors", c) for c in A.CODE_ERRORS] + [(c, "Environment", c) for c in A.ENV_ERRORS]
    rows5 += [("Code Errors subtotal", "Code Errors", "Subtotal"), ("Environment subtotal", "Environment", "Subtotal")]
    for name, group, cat in rows5:
        add(f"Table 5 {name} count", paper["table5_errors"]["counts"][name], int(cell(group, cat, "count")))
        add(f"Table 5 {name} %", paper["table5_errors"]["pct"][name], float(cell(group, cat, "pct")))
    add("Table 5 total failures", paper["table5_errors"]["counts"]["Total"],
        int(t5[t5.group == "Total"]["count"].iloc[0]))

    ea = A.errors_by_agent(df)
    for agent, v in paper["figure4_by_agent"].items():
        for k, val in v.items():
            add(f"Figure 4 {agent} {k}", val, int(ea.loc[k, agent]))

    gaps = A.by_agent_language(df).set_index(["agent", "language"])
    n_gap = int(df.has_gap.sum())
    cg = paper["completeness_gap"]
    add("Completeness gap k=0 artifacts", cg["k0"], len(df) - n_gap)
    add("Completeness gap k=1 artifacts", cg["k1"], n_gap)
    add("Completeness gap k=0 share %", cg["k0_pct"], round(100 * (len(df) - n_gap) / len(df)), tol=0)
    add("Completeness gap k=1 share %", cg["k1_pct"], round(100 * n_gap / len(df)), tol=0)
    add("Completeness gap max", cg["max_gap"], int(df.gap.max()))
    for key, val in paper["completeness_gap"]["per_cell"].items():
        agent, lang = key.split("|")
        add(f"Figure 5 {agent} {lang} artifacts with gap", val, int(gaps.loc[(agent, lang), "with_gap"]))

    rt = A.runtime_expansion(df).set_index("language")
    for lang, v in paper["figure6_runtime"].items():
        if lang == "weighted_multiplier":
            continue
        for k in ("claimed", "runtime", "multiplier"):
            add(f"Figure 6 {lang} {k}", v[k], float(rt.loc[lang, k]))
    add("Weighted runtime multiplier (x)", paper["figure6_runtime"]["weighted_multiplier"],
        round(rt.attrs["weighted_multiplier"]), tol=0)
    return rows


def figures(df, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out.mkdir(parents=True, exist_ok=True)
    t4 = A.by_agent_language(df)
    langs = ["Python", "Java", "JavaScript"]
    agents = ["Claude", "Codex", "Gemini"]

    # Figure 3: success-rate heatmap
    m = np.array([[t4[(t4.agent == a) & (t4.language == l)].rate.iloc[0] for l in langs] for a in agents])
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(m, cmap="RdYlGn", vmin=0, vmax=100)
    ax.set_xticks(range(3), langs)
    ax.set_yticks(range(3), agents)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{m[i, j]:.1f}%", ha="center", va="center")
    ax.set_xlabel("Programming language")
    ax.set_ylabel("Coding agent")
    ax.set_title("Execution success rates")
    fig.colorbar(im, ax=ax, label="Success rate (%)")
    fig.tight_layout()
    fig.savefig(out / "figure3_success_heatmap.png", dpi=200)
    plt.close(fig)

    # Figure 4: error composition by agent
    ea = A.errors_by_agent(df)
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(3)
    w = 0.38
    for offset, cats in [(-w / 2, A.CODE_ERRORS), (w / 2, A.ENV_ERRORS)]:
        bottom = np.zeros(3)
        for c in cats:
            vals = ea.loc[c, agents].to_numpy()
            ax.bar(x + offset, vals, w, bottom=bottom, label=c, edgecolor="black", linewidth=0.5)
            bottom += vals
        for i, b in enumerate(bottom):
            ax.text(x[i] + offset, b + 0.3, str(int(b)), ha="center", va="bottom")
    ax.set_xticks(x, [f"{a}\nCODE | ENV" for a in agents])
    ax.set_ylabel("Failed artifacts")
    ax.set_title("Error composition: code vs environment")
    ax.set_ylim(0, ea.loc[["CODE", "ENV"]].to_numpy().max() * 1.45)
    ax.legend(fontsize=8, ncol=3, loc="upper center")
    fig.tight_layout()
    fig.savefig(out / "figure4_error_composition.png", dpi=200)
    plt.close(fig)

    # Figure 5: completeness gaps
    fig, ax = plt.subplots(figsize=(8, 3.5))
    labels, vals = [], []
    for a in agents:
        for l in langs:
            r = t4[(t4.agent == a) & (t4.language == l)].iloc[0]
            labels.append(f"{a}\n{l}")
            vals.append(r.with_gap)
            if r.with_gap:
                ax.text(len(vals) - 1, r.with_gap + 0.05, f"{r.with_gap}/{r.n}", ha="center", va="bottom", fontsize=8)
    ax.bar(range(9), vals, color=[c for c in ("C0", "C1", "C2") for _ in range(3)])
    ax.set_xticks(range(9), labels, fontsize=8)
    ax.set_ylabel("Artifacts with undeclared deps")
    ax.set_title("Dependency completeness gaps")
    fig.tight_layout()
    fig.savefig(out / "figure5_completeness_gaps.png", dpi=200)
    plt.close(fig)

    # Figure 6: claimed vs runtime dependencies
    rt = A.runtime_expansion(df).set_index("language").loc[langs]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.5))
    x = np.arange(3)
    ax1.bar(x - 0.2, rt.claimed, 0.4, label="Claimed")
    ax1.bar(x + 0.2, rt.runtime, 0.4, label="Runtime")
    for i in range(3):
        ax1.text(i - 0.2, rt.claimed.iloc[i], f"{rt.claimed.iloc[i]:.1f}", ha="center", va="bottom", fontsize=8)
        ax1.text(i + 0.2, rt.runtime.iloc[i], f"{rt.runtime.iloc[i]:.1f}", ha="center", va="bottom", fontsize=8)
    ax1.set_xticks(x, langs)
    ax1.set_ylabel("Average number of dependencies")
    ax1.legend()
    ax2.bar(x, rt.multiplier, color="C3")
    for i in range(3):
        ax2.text(i, rt.multiplier.iloc[i], f"{rt.multiplier.iloc[i]:.1f}x", ha="center", va="bottom")
    ax2.set_xticks(x, langs)
    ax2.set_ylabel("Multiplier (runtime / claimed)")
    fig.tight_layout()
    fig.savefig(out / "figure6_runtime_expansion.png", dpi=200)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", type=Path, default=ROOT / "data" / "results")
    ap.add_argument("--out", type=Path, default=ROOT / "results")
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()

    import pandas as pd

    df = A.load(args.data)
    tables = args.out / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    A.by_agent(df).to_csv(tables / "table2_execution_reliability.csv", index=False)
    A.by_language(df).to_csv(tables / "table3_language.csv", index=False)
    A.by_agent_language(df).to_csv(tables / "table4_agent_language.csv", index=False)
    A.error_table(df).to_csv(tables / "table5_error_distribution.csv", index=False)
    A.errors_by_agent(df).to_csv(tables / "figure4_errors_by_agent.csv")
    A.runtime_expansion(df).to_csv(tables / "figure6_runtime_expansion.csv", index=False)
    if not args.no_figures:
        figures(df, args.out / "figures")

    paper = json.loads((ROOT / "results" / "paper_values.json").read_text(encoding="utf-8"))
    cmp = pd.DataFrame(compare(paper, df))
    cmp.to_csv(args.out / "comparison.csv", index=False)
    with pd.option_context("display.max_rows", None, "display.width", 140, "display.max_colwidth", 60):
        print(cmp.to_string(index=False))
    bad = cmp[cmp.match != "yes"]
    print(f"\n{len(cmp) - len(bad)}/{len(cmp)} values match the paper.")
    if len(bad):
        print("Values that differ:\n" + bad.to_string(index=False))
    return 1 if len(bad) else 0


if __name__ == "__main__":
    sys.exit(main())
