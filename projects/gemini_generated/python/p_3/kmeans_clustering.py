import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import csv

def find_optimal_k(data):
    """
    Uses the elbow method to find the optimal number of clusters (K).
    Saves a plot of the elbow curve.
    """
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(data)
        wcss.append(kmeans.inertia_)
    
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters (K)')
    plt.ylabel('WCSS (Within-Cluster Sum of Squares)')
    plt.grid(True)
    plt.savefig('elbow_plot.png')
    plt.close()
    print("Elbow method plot saved as elbow_plot.png")

def run_kmeans(data, n_clusters):
    """
    Performs K-means clustering and saves a visualization of the clusters.
    """
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
    pred_y = kmeans.fit_predict(data)
    
    plt.figure(figsize=(10, 7))
    plt.scatter(data[:, 0], data[:, 1], c=pred_y, s=50, cmap='viridis')
    
    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.75, marker='X')
    plt.title(f'K-Means Clustering with {n_clusters} Clusters')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.grid(True)
    plt.savefig('clusters_plot.png')
    plt.close()
    print(f"Cluster visualization saved as clusters_plot.png")
    
    return pred_y

def save_assignments(data, labels, filename="cluster_assignments.csv"):
    """
    Saves the data points and their assigned cluster labels to a CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Feature_1', 'Feature_2', 'Cluster_ID'])
        for i in range(len(data)):
            writer.writerow([data[i][0], data[i][1], labels[i]])
    print(f"Cluster assignments saved to {filename}")

if __name__ == "__main__":
    # 1. Generate synthetic data for demonstration
    # This makes the script reproducible without needing an external data file.
    X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)
    
    # 2. Find the optimal K using the elbow method
    find_optimal_k(X)
    
    # From the elbow_plot.png, we can observe that the "elbow" is at K=4.
    # We will use this value for clustering.
    optimal_k = 4
    
    # 3. Run K-means with the optimal K and get cluster labels
    cluster_labels = run_kmeans(X, optimal_k)
    
    # 4. Save the results to a CSV file
    save_assignments(X, cluster_labels)

