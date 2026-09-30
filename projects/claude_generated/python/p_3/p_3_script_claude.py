"""
K-means Clustering Script with Elbow Method and Visualization
Clusters similar data points and provides visualizations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_blobs
import argparse
import os
from datetime import datetime


def generate_sample_data(n_samples=300, n_features=2, n_centers=4, random_state=42):
    """
    Generate sample data for clustering demonstration.

    Args:
        n_samples: Number of data points
        n_features: Number of features
        n_centers: Actual number of clusters in data
        random_state: Random seed for reproducibility

    Returns:
        X: Feature matrix
        y_true: True cluster labels (for comparison)
    """
    X, y_true = make_blobs(
        n_samples=n_samples,
        n_features=n_features,
        centers=n_centers,
        cluster_std=0.60,
        random_state=random_state
    )
    return X, y_true


def load_data_from_csv(file_path):
    """
    Load data from CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        X: Feature matrix (numpy array)
        df: Original dataframe
    """
    df = pd.read_csv(file_path)
    X = df.select_dtypes(include=[np.number]).values
    return X, df


def calculate_elbow_method(X, max_k=10):
    """
    Calculate inertia (WCSS) for different values of K.

    Args:
        X: Feature matrix
        max_k: Maximum number of clusters to test

    Returns:
        inertias: List of inertia values
        k_range: Range of K values tested
    """
    inertias = []
    k_range = range(1, max_k + 1)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)

    return inertias, k_range


def plot_elbow_curve(inertias, k_range, output_dir='output'):
    """
    Plot the elbow curve for K selection.

    Args:
        inertias: List of inertia values
        k_range: Range of K values
        output_dir: Directory to save the plot
    """
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.plot(k_range, inertias, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Number of Clusters (K)', fontsize=12)
    plt.ylabel('Inertia (WCSS)', fontsize=12)
    plt.title('Elbow Method for Optimal K Selection', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xticks(k_range)

    output_path = os.path.join(output_dir, 'elbow_curve.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Elbow curve saved to: {output_path}")
    plt.close()


def perform_clustering(X, n_clusters, random_state=42):
    """
    Perform K-means clustering.

    Args:
        X: Feature matrix
        n_clusters: Number of clusters
        random_state: Random seed

    Returns:
        kmeans: Fitted KMeans model
        labels: Cluster assignments
        centers: Cluster centers
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_

    return kmeans, labels, centers


def visualize_clusters_2d(X, labels, centers, output_dir='output'):
    """
    Visualize clusters for 2D data.

    Args:
        X: Feature matrix (must be 2D)
        labels: Cluster assignments
        centers: Cluster centers
        output_dir: Directory to save the plot
    """
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(12, 8))

    # Plot data points
    scatter = plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis',
                         s=50, alpha=0.6, edgecolors='black', linewidth=0.5)

    # Plot cluster centers
    plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='X',
               s=300, edgecolors='black', linewidth=2, label='Centroids')

    plt.xlabel('Feature 1', fontsize=12)
    plt.ylabel('Feature 2', fontsize=12)
    plt.title('K-means Clustering Results', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, label='Cluster')
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = os.path.join(output_dir, 'clusters_visualization.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Cluster visualization saved to: {output_path}")
    plt.close()


def visualize_clusters_3d(X, labels, centers, output_dir='output'):
    """
    Visualize clusters for 3D data.

    Args:
        X: Feature matrix (must be 3D)
        labels: Cluster assignments
        centers: Cluster centers
        output_dir: Directory to save the plot
    """
    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot data points
    scatter = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=labels, cmap='viridis',
                        s=50, alpha=0.6, edgecolors='black', linewidth=0.5)

    # Plot cluster centers
    ax.scatter(centers[:, 0], centers[:, 1], centers[:, 2], c='red',
              marker='X', s=300, edgecolors='black', linewidth=2, label='Centroids')

    ax.set_xlabel('Feature 1', fontsize=12)
    ax.set_ylabel('Feature 2', fontsize=12)
    ax.set_zlabel('Feature 3', fontsize=12)
    ax.set_title('K-means Clustering Results (3D)', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, label='Cluster', ax=ax, shrink=0.5)
    ax.legend()

    output_path = os.path.join(output_dir, 'clusters_visualization_3d.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"3D cluster visualization saved to: {output_path}")
    plt.close()


def save_cluster_assignments(X, labels, centers, kmeans, output_dir='output'):
    """
    Save cluster assignments and statistics to CSV files.

    Args:
        X: Feature matrix
        labels: Cluster assignments
        centers: Cluster centers
        kmeans: Fitted KMeans model
        output_dir: Directory to save files
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save cluster assignments
    df_assignments = pd.DataFrame(X, columns=[f'Feature_{i+1}' for i in range(X.shape[1])])
    df_assignments['Cluster'] = labels
    df_assignments['Distance_to_Centroid'] = [
        np.linalg.norm(X[i] - centers[labels[i]]) for i in range(len(X))
    ]

    assignments_path = os.path.join(output_dir, 'cluster_assignments.csv')
    df_assignments.to_csv(assignments_path, index=False)
    print(f"Cluster assignments saved to: {assignments_path}")

    # Save cluster centers
    df_centers = pd.DataFrame(centers, columns=[f'Feature_{i+1}' for i in range(centers.shape[1])])
    df_centers['Cluster'] = range(len(centers))

    centers_path = os.path.join(output_dir, 'cluster_centers.csv')
    df_centers.to_csv(centers_path, index=False)
    print(f"Cluster centers saved to: {centers_path}")

    # Save cluster statistics
    stats = []
    for i in range(len(centers)):
        cluster_points = X[labels == i]
        stats.append({
            'Cluster': i,
            'Size': len(cluster_points),
            'Percentage': f"{len(cluster_points) / len(X) * 100:.2f}%",
            'Inertia': kmeans.inertia_
        })

    df_stats = pd.DataFrame(stats)
    stats_path = os.path.join(output_dir, 'cluster_statistics.csv')
    df_stats.to_csv(stats_path, index=False)
    print(f"Cluster statistics saved to: {stats_path}")

    # Print summary
    print("\n" + "="*50)
    print("CLUSTERING SUMMARY")
    print("="*50)
    print(f"Total data points: {len(X)}")
    print(f"Number of clusters: {len(centers)}")
    print(f"Total inertia: {kmeans.inertia_:.2f}")
    print("\nCluster sizes:")
    print(df_stats[['Cluster', 'Size', 'Percentage']].to_string(index=False))
    print("="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='K-means Clustering with Elbow Method and Visualization'
    )
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to input CSV file (if not provided, sample data will be generated)'
    )
    parser.add_argument(
        '--clusters',
        type=int,
        default=None,
        help='Number of clusters (if not provided, will use elbow method)'
    )
    parser.add_argument(
        '--max-k',
        type=int,
        default=10,
        help='Maximum K value for elbow method (default: 10)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    parser.add_argument(
        '--normalize',
        action='store_true',
        help='Normalize features using StandardScaler'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=300,
        help='Number of sample data points to generate (default: 300)'
    )
    parser.add_argument(
        '--features',
        type=int,
        default=2,
        help='Number of features for sample data (default: 2, max: 3 for visualization)'
    )

    args = parser.parse_args()

    print("="*50)
    print("K-MEANS CLUSTERING SCRIPT")
    print("="*50 + "\n")

    # Load or generate data
    if args.input:
        print(f"Loading data from: {args.input}")
        X, df_original = load_data_from_csv(args.input)
        print(f"Loaded {len(X)} data points with {X.shape[1]} features\n")
    else:
        print("Generating sample data...")
        X, y_true = generate_sample_data(
            n_samples=args.samples,
            n_features=args.features,
            n_centers=4
        )
        print(f"Generated {len(X)} data points with {X.shape[1]} features\n")

    # Normalize data if requested
    if args.normalize:
        print("Normalizing features...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X = X_scaled
        print("Features normalized\n")

    # Perform elbow method
    print(f"Calculating elbow method (K=1 to K={args.max_k})...")
    inertias, k_range = calculate_elbow_method(X, max_k=args.max_k)
    plot_elbow_curve(inertias, k_range, output_dir=args.output_dir)
    print()

    # Determine optimal K
    if args.clusters:
        n_clusters = args.clusters
        print(f"Using user-specified K={n_clusters}\n")
    else:
        # Simple elbow detection (you can improve this with more sophisticated methods)
        # For demonstration, we'll use K=4 as default
        n_clusters = 4
        print(f"Using K={n_clusters} (examine elbow curve for optimal K)\n")

    # Perform clustering
    print(f"Performing K-means clustering with K={n_clusters}...")
    kmeans, labels, centers = perform_clustering(X, n_clusters)
    print("Clustering complete\n")

    # Visualize clusters
    print("Creating visualizations...")
    if X.shape[1] == 2:
        visualize_clusters_2d(X, labels, centers, output_dir=args.output_dir)
    elif X.shape[1] == 3:
        visualize_clusters_3d(X, labels, centers, output_dir=args.output_dir)
    else:
        print(f"Visualization not supported for {X.shape[1]}D data (only 2D and 3D supported)")
    print()

    # Save results
    print("Saving cluster assignments and statistics...")
    save_cluster_assignments(X, labels, centers, kmeans, output_dir=args.output_dir)

    print("\nAll tasks completed successfully!")


if __name__ == '__main__':
    main()
