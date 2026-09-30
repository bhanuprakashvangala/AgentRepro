# recommendation_system.py

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr
from scipy.sparse import csr_matrix
import warnings
warnings.filterwarnings('ignore')


class CollaborativeFilteringRecommender:
    """
    A complete recommendation system implementing both user-based and item-based
    collaborative filtering with cosine and Pearson similarity metrics.
    """

    def __init__(self, ratings_data=None):
        """
        Initialize the recommender system.

        Parameters:
        -----------
        ratings_data : pd.DataFrame
            DataFrame with columns: ['user_id', 'item_id', 'rating']
        """
        self.ratings_data = ratings_data
        self.user_item_matrix = None
        self.user_similarity_cosine = None
        self.user_similarity_pearson = None
        self.item_similarity_cosine = None
        self.item_similarity_pearson = None

    def create_user_item_matrix(self):
        """Create user-item rating matrix from ratings data."""
        if self.ratings_data is None:
            raise ValueError("No ratings data provided")

        self.user_item_matrix = self.ratings_data.pivot_table(
            index='user_id',
            columns='item_id',
            values='rating'
        ).fillna(0)

        print(f"User-Item Matrix Shape: {self.user_item_matrix.shape}")
        return self.user_item_matrix

    def calculate_cosine_similarity(self, matrix, axis='user'):
        """
        Calculate cosine similarity.

        Parameters:
        -----------
        matrix : pd.DataFrame
            User-item matrix
        axis : str
            'user' for user-based, 'item' for item-based

        Returns:
        --------
        pd.DataFrame : Similarity matrix
        """
        if axis == 'user':
            similarity = cosine_similarity(matrix)
            similarity_df = pd.DataFrame(
                similarity,
                index=matrix.index,
                columns=matrix.index
            )
        else:  # item-based
            similarity = cosine_similarity(matrix.T)
            similarity_df = pd.DataFrame(
                similarity,
                index=matrix.columns,
                columns=matrix.columns
            )

        return similarity_df

    def calculate_pearson_similarity(self, matrix, axis='user'):
        """
        Calculate Pearson correlation similarity.

        Parameters:
        -----------
        matrix : pd.DataFrame
            User-item matrix
        axis : str
            'user' for user-based, 'item' for item-based

        Returns:
        --------
        pd.DataFrame : Similarity matrix
        """
        if axis == 'user':
            similarity_df = matrix.T.corr(method='pearson').fillna(0)
        else:  # item-based
            similarity_df = matrix.corr(method='pearson').fillna(0)

        return similarity_df

    def fit(self):
        """Calculate all similarity matrices."""
        if self.user_item_matrix is None:
            self.create_user_item_matrix()

        print("Calculating User-Based Cosine Similarity...")
        self.user_similarity_cosine = self.calculate_cosine_similarity(
            self.user_item_matrix, axis='user'
        )

        print("Calculating User-Based Pearson Similarity...")
        self.user_similarity_pearson = self.calculate_pearson_similarity(
            self.user_item_matrix, axis='user'
        )

        print("Calculating Item-Based Cosine Similarity...")
        self.item_similarity_cosine = self.calculate_cosine_similarity(
            self.user_item_matrix, axis='item'
        )

        print("Calculating Item-Based Pearson Similarity...")
        self.item_similarity_pearson = self.calculate_pearson_similarity(
            self.user_item_matrix, axis='item'
        )

        print("All similarity matrices calculated successfully!")
        return self

    def predict_user_based(self, user_id, item_id, similarity_type='cosine', k=5):
        """
        Predict rating using user-based collaborative filtering.

        Parameters:
        -----------
        user_id : int
            Target user ID
        item_id : int
            Target item ID
        similarity_type : str
            'cosine' or 'pearson'
        k : int
            Number of similar users to consider

        Returns:
        --------
        float : Predicted rating
        """
        if user_id not in self.user_item_matrix.index:
            return self.user_item_matrix.values.mean()

        if item_id not in self.user_item_matrix.columns:
            return self.user_item_matrix.loc[user_id].replace(0, np.nan).mean()

        # Get similarity scores
        if similarity_type == 'cosine':
            similarities = self.user_similarity_cosine.loc[user_id]
        else:
            similarities = self.user_similarity_pearson.loc[user_id]

        # Get users who rated this item
        item_ratings = self.user_item_matrix[item_id]
        rated_users = item_ratings[item_ratings > 0].index

        # Filter similarities for users who rated the item
        valid_similarities = similarities[rated_users]

        # Get top-k similar users
        if len(valid_similarities) == 0:
            return self.user_item_matrix.values.mean()

        top_k_users = valid_similarities.nlargest(k + 1)[1:k + 1]  # Exclude self

        if len(top_k_users) == 0 or top_k_users.sum() == 0:
            return self.user_item_matrix.values.mean()

        # Calculate weighted average
        numerator = sum(top_k_users[user] * item_ratings[user] for user in top_k_users.index)
        denominator = sum(abs(top_k_users))

        if denominator == 0:
            return self.user_item_matrix.values.mean()

        return numerator / denominator

    def predict_item_based(self, user_id, item_id, similarity_type='cosine', k=5):
        """
        Predict rating using item-based collaborative filtering.

        Parameters:
        -----------
        user_id : int
            Target user ID
        item_id : int
            Target item ID
        similarity_type : str
            'cosine' or 'pearson'
        k : int
            Number of similar items to consider

        Returns:
        --------
        float : Predicted rating
        """
        if user_id not in self.user_item_matrix.index:
            return self.user_item_matrix.values.mean()

        if item_id not in self.user_item_matrix.columns:
            return self.user_item_matrix.loc[user_id].replace(0, np.nan).mean()

        # Get similarity scores
        if similarity_type == 'cosine':
            similarities = self.item_similarity_cosine.loc[item_id]
        else:
            similarities = self.item_similarity_pearson.loc[item_id]

        # Get items rated by this user
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0].index

        # Filter similarities for items rated by the user
        valid_similarities = similarities[rated_items]

        # Get top-k similar items
        if len(valid_similarities) == 0:
            return self.user_item_matrix.values.mean()

        top_k_items = valid_similarities.nlargest(k + 1)[1:k + 1]  # Exclude self

        if len(top_k_items) == 0 or top_k_items.sum() == 0:
            return self.user_item_matrix.values.mean()

        # Calculate weighted average
        numerator = sum(top_k_items[item] * user_ratings[item] for item in top_k_items.index)
        denominator = sum(abs(top_k_items))

        if denominator == 0:
            return self.user_item_matrix.values.mean()

        return numerator / denominator

    def recommend_top_n(self, user_id, n=10, method='user', similarity_type='cosine', k=5):
        """
        Generate top-N recommendations for a user.

        Parameters:
        -----------
        user_id : int
            Target user ID
        n : int
            Number of recommendations to generate
        method : str
            'user' for user-based, 'item' for item-based
        similarity_type : str
            'cosine' or 'pearson'
        k : int
            Number of neighbors to consider

        Returns:
        --------
        pd.DataFrame : Top-N recommendations with predicted ratings
        """
        if user_id not in self.user_item_matrix.index:
            print(f"User {user_id} not found in the dataset")
            return pd.DataFrame()

        # Get items not yet rated by the user
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index

        if len(unrated_items) == 0:
            print(f"User {user_id} has rated all items")
            return pd.DataFrame()

        # Predict ratings for unrated items
        predictions = []
        for item_id in unrated_items:
            if method == 'user':
                predicted_rating = self.predict_user_based(
                    user_id, item_id, similarity_type, k
                )
            else:
                predicted_rating = self.predict_item_based(
                    user_id, item_id, similarity_type, k
                )

            predictions.append({
                'item_id': item_id,
                'predicted_rating': predicted_rating
            })

        # Sort by predicted rating and return top-N
        recommendations_df = pd.DataFrame(predictions)
        recommendations_df = recommendations_df.sort_values(
            'predicted_rating', ascending=False
        ).head(n)

        return recommendations_df.reset_index(drop=True)

    def evaluate_predictions(self, test_data, method='user', similarity_type='cosine', k=5):
        """
        Evaluate prediction accuracy on test data.

        Parameters:
        -----------
        test_data : pd.DataFrame
            Test data with columns: ['user_id', 'item_id', 'rating']
        method : str
            'user' for user-based, 'item' for item-based
        similarity_type : str
            'cosine' or 'pearson'
        k : int
            Number of neighbors to consider

        Returns:
        --------
        dict : Dictionary with RMSE and MAE metrics
        """
        predictions = []
        actuals = []

        for _, row in test_data.iterrows():
            user_id = row['user_id']
            item_id = row['item_id']
            actual_rating = row['rating']

            if method == 'user':
                predicted_rating = self.predict_user_based(
                    user_id, item_id, similarity_type, k
                )
            else:
                predicted_rating = self.predict_item_based(
                    user_id, item_id, similarity_type, k
                )

            predictions.append(predicted_rating)
            actuals.append(actual_rating)

        # Calculate metrics
        predictions = np.array(predictions)
        actuals = np.array(actuals)

        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))
        mae = np.mean(np.abs(predictions - actuals))

        return {
            'RMSE': rmse,
            'MAE': mae
        }


def generate_sample_data(n_users=100, n_items=50, n_ratings=1000, rating_scale=(1, 5)):
    """
    Generate sample ratings data for demonstration.

    Parameters:
    -----------
    n_users : int
        Number of users
    n_items : int
        Number of items
    n_ratings : int
        Number of ratings to generate
    rating_scale : tuple
        Min and max rating values

    Returns:
    --------
    pd.DataFrame : Ratings data
    """
    np.random.seed(42)

    user_ids = np.random.randint(1, n_users + 1, n_ratings)
    item_ids = np.random.randint(1, n_items + 1, n_ratings)
    ratings = np.random.randint(rating_scale[0], rating_scale[1] + 1, n_ratings)

    data = pd.DataFrame({
        'user_id': user_ids,
        'item_id': item_ids,
        'rating': ratings
    })

    # Remove duplicates (keep first rating)
    data = data.drop_duplicates(subset=['user_id', 'item_id'], keep='first')

    return data


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("COLLABORATIVE FILTERING RECOMMENDATION SYSTEM")
    print("=" * 70)
    print()

    # Generate sample data
    print("Generating sample ratings data...")
    ratings_data = generate_sample_data(n_users=100, n_items=50, n_ratings=2000)
    print(f"Generated {len(ratings_data)} ratings")
    print(f"Users: {ratings_data['user_id'].nunique()}")
    print(f"Items: {ratings_data['item_id'].nunique()}")
    print()

    # Split data into train/test
    train_size = int(0.8 * len(ratings_data))
    train_data = ratings_data.iloc[:train_size]
    test_data = ratings_data.iloc[train_size:]

    print(f"Train set: {len(train_data)} ratings")
    print(f"Test set: {len(test_data)} ratings")
    print()

    # Initialize and fit the recommender
    print("Initializing Collaborative Filtering Recommender...")
    recommender = CollaborativeFilteringRecommender(train_data)
    recommender.fit()
    print()

    # Test user for recommendations
    test_user_id = 5

    print("=" * 70)
    print(f"GENERATING RECOMMENDATIONS FOR USER {test_user_id}")
    print("=" * 70)
    print()

    # User-Based Cosine Similarity
    print("1. User-Based Collaborative Filtering (Cosine Similarity)")
    print("-" * 70)
    user_cosine_recs = recommender.recommend_top_n(
        test_user_id, n=10, method='user', similarity_type='cosine', k=5
    )
    print(user_cosine_recs)
    print()

    # User-Based Pearson Similarity
    print("2. User-Based Collaborative Filtering (Pearson Similarity)")
    print("-" * 70)
    user_pearson_recs = recommender.recommend_top_n(
        test_user_id, n=10, method='user', similarity_type='pearson', k=5
    )
    print(user_pearson_recs)
    print()

    # Item-Based Cosine Similarity
    print("3. Item-Based Collaborative Filtering (Cosine Similarity)")
    print("-" * 70)
    item_cosine_recs = recommender.recommend_top_n(
        test_user_id, n=10, method='item', similarity_type='cosine', k=5
    )
    print(item_cosine_recs)
    print()

    # Item-Based Pearson Similarity
    print("4. Item-Based Collaborative Filtering (Pearson Similarity)")
    print("-" * 70)
    item_pearson_recs = recommender.recommend_top_n(
        test_user_id, n=10, method='item', similarity_type='pearson', k=5
    )
    print(item_pearson_recs)
    print()

    # Evaluate on test set
    print("=" * 70)
    print("EVALUATION ON TEST SET")
    print("=" * 70)
    print()

    print("Evaluating User-Based Cosine Similarity...")
    metrics_user_cosine = recommender.evaluate_predictions(
        test_data, method='user', similarity_type='cosine', k=5
    )
    print(f"RMSE: {metrics_user_cosine['RMSE']:.4f}")
    print(f"MAE: {metrics_user_cosine['MAE']:.4f}")
    print()

    print("Evaluating User-Based Pearson Similarity...")
    metrics_user_pearson = recommender.evaluate_predictions(
        test_data, method='user', similarity_type='pearson', k=5
    )
    print(f"RMSE: {metrics_user_pearson['RMSE']:.4f}")
    print(f"MAE: {metrics_user_pearson['MAE']:.4f}")
    print()

    print("Evaluating Item-Based Cosine Similarity...")
    metrics_item_cosine = recommender.evaluate_predictions(
        test_data, method='item', similarity_type='cosine', k=5
    )
    print(f"RMSE: {metrics_item_cosine['RMSE']:.4f}")
    print(f"MAE: {metrics_item_cosine['MAE']:.4f}")
    print()

    print("Evaluating Item-Based Pearson Similarity...")
    metrics_item_pearson = recommender.evaluate_predictions(
        test_data, method='item', similarity_type='pearson', k=5
    )
    print(f"RMSE: {metrics_item_pearson['RMSE']:.4f}")
    print(f"MAE: {metrics_item_pearson['MAE']:.4f}")
    print()

    # Summary comparison
    print("=" * 70)
    print("SUMMARY COMPARISON")
    print("=" * 70)
    print()

    comparison = pd.DataFrame({
        'Method': [
            'User-Based (Cosine)',
            'User-Based (Pearson)',
            'Item-Based (Cosine)',
            'Item-Based (Pearson)'
        ],
        'RMSE': [
            metrics_user_cosine['RMSE'],
            metrics_user_pearson['RMSE'],
            metrics_item_cosine['RMSE'],
            metrics_item_pearson['RMSE']
        ],
        'MAE': [
            metrics_user_cosine['MAE'],
            metrics_user_pearson['MAE'],
            metrics_item_cosine['MAE'],
            metrics_item_pearson['MAE']
        ]
    })

    print(comparison.to_string(index=False))
    print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
