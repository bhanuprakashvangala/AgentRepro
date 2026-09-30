# K-means Clustering Toolkit

This script performs K-means clustering on tabular data, helps select an appropriate number of clusters via the elbow method, and produces both graphical and tabular outputs.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Supply a CSV that contains numeric columns (non-numeric columns are ignored). Example run:

```bash
python kmeans_cluster.py --input data.csv --output-clusters clustered.csv --elbow-plot elbow.png --cluster-plot clusters.png
```

Key options:
- `--clusters`: Manually set the number of clusters. If omitted, the script scans `--min-k`..`--max-k` and picks an elbow-based value.
- `--min-k` / `--max-k`: Range of cluster counts for the elbow method (defaults 2..8).
- `--no-scale`: Disable standard scaling if your data is already normalized.
- `--encoding`: Override CSV encoding (default `utf-8`).

Outputs:
1. `clustered.csv` – original numeric columns plus a `cluster` label per row.
2. `elbow.png` – inertia vs. cluster count chart (only when auto-selecting `k`).
3. `clusters.png` – 2D visualization of the clusters (uses PCA when needed).
