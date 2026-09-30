#!/usr/bin/env python3
"""Command-line utility for K-means clustering with elbow analysis and visualization."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use("Agg")  # Enable headless environment rendering
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Perform K-means clustering on a CSV dataset, visualize results, and save outputs."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file with numeric columns.")
    parser.add_argument(
        "--output-clusters",
        default="cluster_assignments.csv",
        help="Path to save CSV with original data and cluster labels.",
    )
    parser.add_argument(
        "--elbow-plot",
        default="elbow_plot.png",
        help="Filename for the elbow method plot.",
    )
    parser.add_argument(
        "--cluster-plot",
        default="cluster_plot.png",
        help="Filename for the 2D cluster visualization.",
    )
    parser.add_argument(
        "--min-k",
        type=int,
        default=2,
        help="Minimum number of clusters to evaluate for the elbow method (default: 2).",
    )
    parser.add_argument(
        "--max-k",
        type=int,
        default=8,
        help="Maximum number of clusters to evaluate for the elbow method (default: 8).",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=None,
        help="Optional fixed number of clusters to use. Overrides elbow selection when provided.",
    )
    parser.add_argument(
        "--no-scale",
        action="store_true",
        help="Disable feature scaling before clustering.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding of the input CSV file (default: utf-8).",
    )
    return parser.parse_args()


def load_dataset(path: Path, encoding: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    try:
        return pd.read_csv(path, encoding=encoding)
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(f"Unable to read CSV file: {path} ({exc})") from exc


def select_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"]).copy()
    if numeric_df.empty:
        raise ValueError("No numeric columns found in the dataset. Provide numeric features for clustering.")
    numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan).dropna()
    if numeric_df.empty:
        raise ValueError("Numeric data contains only NaN or infinite values after cleaning.")
    return numeric_df


def scale_features(features: pd.DataFrame, enable_scaling: bool) -> Tuple[np.ndarray, StandardScaler | None]:
    if not enable_scaling:
        return features.to_numpy(), None
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    return scaled, scaler


def compute_elbow_curve(data: np.ndarray, min_k: int, max_k: int, random_state: int = 42) -> Tuple[List[int], List[float]]:
    if min_k < 1 or max_k < 1:
        raise ValueError("Cluster counts must be positive integers.")
    if min_k >= max_k:
        raise ValueError("--max-k must be greater than --min-k for elbow computation.")
    k_values: List[int] = list(range(min_k, max_k + 1))
    inertias: List[float] = []
    for k in k_values:
        model = KMeans(n_clusters=k, random_state=random_state, n_init="auto")
        model.fit(data)
        inertias.append(model.inertia_)
    return k_values, inertias


def choose_k_from_elbow(k_values: List[int], inertias: List[float]) -> int:
    if len(k_values) <= 2:
        return k_values[0]
    first_diff = np.diff(inertias)
    second_diff = np.diff(first_diff)
    if len(second_diff) == 0:
        return k_values[0]
    best_index = int(np.argmax(np.abs(second_diff))) + 2
    best_index = min(best_index, len(k_values) - 1)
    return k_values[best_index]


def plot_elbow(k_values: List[int], inertias: List[float], output_path: Path) -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(k_values, inertias, marker="o")
    plt.title("Elbow Method for Optimal k")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_clusters(data: np.ndarray, labels: np.ndarray, output_path: Path) -> None:
    if data.shape[1] > 2:
        pca = PCA(n_components=2, random_state=42)
        reduced = pca.fit_transform(data)
    else:
        reduced = data
    plt.figure(figsize=(6, 4))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap="tab10", alpha=0.8)
    plt.title("K-means Clusters (2D view)")
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    legend1 = plt.legend(*scatter.legend_elements(), title="Cluster")
    plt.gca().add_artist(legend1)
    plt.savefig(output_path)
    plt.close()


def append_clusters_to_dataframe(original: pd.DataFrame, clusters: np.ndarray) -> pd.DataFrame:
    result = original.copy()
    result = result.loc[: len(clusters) - 1].copy()
    result["cluster"] = clusters
    return result


def main() -> None:
    args = parse_args()

    try:
        input_path = Path(args.input)
        df = load_dataset(input_path, args.encoding)
        numeric_df = select_numeric_features(df)
        scaled_data, _ = scale_features(numeric_df, not args.no_scale)

        if args.clusters is not None:
            if args.clusters < 1:
                raise ValueError("--clusters must be a positive integer when provided.")
            chosen_k = args.clusters
            k_values, inertias = [], []
        else:
            k_values, inertias = compute_elbow_curve(scaled_data, args.min_k, args.max_k)
            chosen_k = choose_k_from_elbow(k_values, inertias)
            plot_elbow(k_values, inertias, Path(args.elbow_plot))

        model = KMeans(n_clusters=chosen_k, random_state=42, n_init="auto")
        model.fit(scaled_data)
        labels = model.labels_

        plot_clusters(scaled_data, labels, Path(args.cluster_plot))

        output_df = append_clusters_to_dataframe(numeric_df, labels)
        output_df.to_csv(args.output_clusters, index=False)

        print(f"K-means clustering completed with k={chosen_k}.")
        if k_values and inertias:
            print(f"Elbow data saved to {args.elbow_plot} (k values: {k_values}).")
        print(f"Cluster visualization saved to {args.cluster_plot}.")
        print(f"Cluster assignments saved to {args.output_clusters}.")

    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
