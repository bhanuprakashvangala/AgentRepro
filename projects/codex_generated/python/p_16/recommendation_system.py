#!/usr/bin/env python3
"""Collaborative filtering recommendation tool supporting user/item similarities."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr

SimilarityMetric = Literal["cosine", "pearson"]


@dataclass
class RecommendationResult:
    user_id: str
    recommendations: List[Tuple[str, float]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collaborative filtering recommender (user-based & item-based)"
    )
    parser.add_argument("--ratings", required=True, help="CSV file with columns user,item,rating")
    parser.add_argument(
        "--users",
        nargs="*",
        default=None,
        help="Optional list of user IDs to generate recommendations for",
    )
    parser.add_argument(
        "--similarity",
        choices=["cosine", "pearson"],
        default="cosine",
        help="Similarity metric to use",
    )
    parser.add_argument(
        "--neighbors",
        type=int,
        default=20,
        help="Number of neighbors to consider",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of recommendations to generate per user",
    )
    parser.add_argument(
        "--mode",
        choices=["user", "item", "both"],
        default="both",
        help="Type of collaborative filtering",
    )
    parser.add_argument(
        "--min-ratings",
        type=int,
        default=1,
        help="Minimum number of ratings required for items/users to be included",
    )
    parser.add_argument(
        "--output",
        default="recommendations.csv",
        help="Output CSV file",
    )
    return parser.parse_args()


def load_ratings(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Ratings file not found: {path}")
    df = pd.read_csv(path)
    expected_cols = {"user", "item", "rating"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(f"Ratings CSV must contain columns: {expected_cols}")
    return df


def filter_min_counts(df: pd.DataFrame, min_ratings: int) -> pd.DataFrame:
    if min_ratings <= 1:
        return df
    user_counts = df["user"].value_counts()
    item_counts = df["item"].value_counts()
    mask = df["user"].isin(user_counts[user_counts >= min_ratings].index) & df[
        "item"
    ].isin(item_counts[item_counts >= min_ratings].index)
    return df[mask]


def build_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return df.pivot_table(index="user", columns="item", values="rating")


def compute_similarity_matrix(matrix: pd.DataFrame, metric: SimilarityMetric) -> pd.DataFrame:
    filled = matrix.fillna(0)
    if metric == "cosine":
        sim = cosine_similarity(filled)
    else:
        arr = filled.to_numpy()
        num_entities = arr.shape[0]
        sim = np.ones((num_entities, num_entities), dtype=float)
        for i in range(num_entities):
            for j in range(i + 1, num_entities):
                a = arr[i]
                b = arr[j]
                if np.count_nonzero(a) == 0 or np.count_nonzero(b) == 0:
                    value = 0.0
                else:
                    value, _ = pearsonr(a, b)
                    if np.isnan(value):
                        value = 0.0
                sim[i, j] = sim[j, i] = value
    return pd.DataFrame(sim, index=matrix.index, columns=matrix.index)


def top_neighbors(similarity: pd.Series, target_id: str, k: int) -> pd.Series:
    filtered = similarity.drop(labels=[target_id], errors="ignore")
    return filtered.sort_values(ascending=False).head(k)


def compute_user_based(
    matrix: pd.DataFrame,
    similarity_matrix: pd.DataFrame,
    user_id: str,
    neighbors_k: int,
    top_n: int,
) -> List[Tuple[str, float]]:
    if user_id not in matrix.index:
        return []
    user_ratings = matrix.loc[user_id]
    to_predict = user_ratings[user_ratings.isna()]
    if to_predict.empty:
        return []

    neighbors = top_neighbors(similarity_matrix.loc[user_id], user_id, neighbors_k)
    if neighbors.empty:
        return []

    neighbor_ratings = matrix.loc[neighbors.index]
    weighted_scores: Dict[str, float] = {}
    similarity_sums: Dict[str, float] = {}

    for neighbor_id, sim_score in neighbors.items():
        ratings = neighbor_ratings.loc[neighbor_id]
        for item, rating in ratings.dropna().items():
            if item in user_ratings and not np.isnan(user_ratings[item]):
                continue
            weighted_scores[item] = weighted_scores.get(item, 0.0) + sim_score * rating
            similarity_sums[item] = similarity_sums.get(item, 0.0) + abs(sim_score)

    predictions = []
    for item, total in weighted_scores.items():
        denom = similarity_sums.get(item, 0.0)
        if denom > 0:
            predictions.append((item, total / denom))

    return sorted(predictions, key=lambda x: x[1], reverse=True)[:top_n]


def compute_item_based(
    matrix: pd.DataFrame,
    similarity_matrix: pd.DataFrame,
    user_id: str,
    neighbors_k: int,
    top_n: int,
) -> List[Tuple[str, float]]:
    if user_id not in matrix.index:
        return []
    user_ratings = matrix.loc[user_id]
    rated_items = user_ratings.dropna()
    unrated_items = user_ratings[user_ratings.isna()].index
    if unrated_items.empty or rated_items.empty:
        return []

    predictions: List[Tuple[str, float]] = []
    for item in unrated_items:
        similarities = similarity_matrix[item].drop(labels=[item], errors="ignore")
        neighbors = similarities.loc[rated_items.index].sort_values(ascending=False).head(neighbors_k)
        if neighbors.empty:
            continue
        numerator = 0.0
        denominator = 0.0
        for neighbor_item, sim_score in neighbors.items():
            rating = rated_items[neighbor_item]
            numerator += sim_score * rating
            denominator += abs(sim_score)
        if denominator > 0:
            predictions.append((item, numerator / denominator))
    return sorted(predictions, key=lambda x: x[1], reverse=True)[:top_n]


def generate_recommendations(
    matrix: pd.DataFrame,
    mode: Literal["user", "item", "both"],
    metric: SimilarityMetric,
    neighbors_k: int,
    top_n: int,
    users: Optional[Iterable[str]] = None,
) -> List[RecommendationResult]:
    targets = list(users) if users else list(matrix.index)
    results: List[RecommendationResult] = []

    if mode in {"user", "both"}:
        user_similarity = compute_similarity_matrix(matrix, metric)
    else:
        user_similarity = None

    if mode in {"item", "both"}:
        item_similarity = compute_similarity_matrix(matrix.T, metric)
    else:
        item_similarity = None

    for user_id in targets:
        combined: Dict[str, float] = {}
        counts: Dict[str, int] = {}

        if user_similarity is not None:
            for item, score in compute_user_based(matrix, user_similarity, user_id, neighbors_k, top_n * 2):
                combined[item] = combined.get(item, 0.0) + score
                counts[item] = counts.get(item, 0) + 1

        if item_similarity is not None:
            for item, score in compute_item_based(matrix, item_similarity, user_id, neighbors_k, top_n * 2):
                combined[item] = combined.get(item, 0.0) + score
                counts[item] = counts.get(item, 0) + 1

        final_scores = [(item, combined[item] / counts[item]) for item in combined if counts[item] > 0]
        final_scores.sort(key=lambda x: x[1], reverse=True)
        results.append(RecommendationResult(user_id=user_id, recommendations=final_scores[:top_n]))

    return results


def save_recommendations(results: List[RecommendationResult], output_path: Path) -> None:
    rows = []
    for result in results:
        for item, score in result.recommendations:
            rows.append({"user": result.user_id, "item": item, "score": score})
    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Recommendations saved to {output_path}")


def main() -> None:
    args = parse_args()
    ratings_df = filter_min_counts(load_ratings(Path(args.ratings)), args.min_ratings)
    if ratings_df.empty:
        print("No ratings remaining after filtering.")
        sys.exit(0)
    matrix = build_matrix(ratings_df)
    users = args.users if args.users else None
    results = generate_recommendations(
        matrix,
        mode=args.mode,
        metric=args.similarity,
        neighbors_k=max(1, args.neighbors),
        top_n=max(1, args.top_n),
        users=users,
    )
    save_recommendations(results, Path(args.output))


if __name__ == "__main__":
    main()
