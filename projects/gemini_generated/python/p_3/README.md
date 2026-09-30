# K-Means Clustering Script

This Python script performs K-means clustering on a sample dataset. It uses the elbow method to determine the optimal number of clusters, visualizes the clusters using matplotlib, and saves the final cluster assignments to a CSV file.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    ```bash
    python kmeans_clustering.py
    ```

## Output

Running the script will generate three files in the same directory:

1.  `elbow_plot.png`: A plot showing the Within-Cluster Sum of Squares (WCSS) for different values of K. This is used to find the optimal number of clusters.
2.  `clusters_plot.png`: A scatter plot visualizing the data points colored by their assigned cluster, with cluster centroids marked in red.
3.  `cluster_assignments.csv`: A CSV file containing the original data features and the final cluster ID assigned to each point.
