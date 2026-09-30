from collections import defaultdict
from surprise import Dataset, KNNWithMeans

def get_top_n_recommendations(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions."""
    # First, map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then, sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

def run_recommendation_system():
    """Loads data, trains models, and generates recommendations."""
    # 1. Load the MovieLens-100k dataset
    # This will download the dataset on the first run
    print("Loading MovieLens 100k dataset...")
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    print("Dataset loaded.")

    # 2. Configure and train the User-Based Collaborative Filtering model
    print("\n--- Training User-Based CF Model (Cosine Similarity) ---")
    sim_options_user = {'name': 'cosine', 'user_based': True}
    algo_user = KNNWithMeans(sim_options=sim_options_user)
    algo_user.fit(trainset)
    print("User-Based model trained.")

    # 3. Configure and train the Item-Based Collaborative Filtering model
    print("\n--- Training Item-Based CF Model (Cosine Similarity) ---")
    sim_options_item = {'name': 'cosine', 'user_based': False}
    algo_item = KNNWithMeans(sim_options=sim_options_item)
    algo_item.fit(trainset)
    print("Item-Based model trained.")

    # 4. Generate recommendations for a sample user
    target_user_id = '196'
    print(f"\n--- Generating Top 10 Recommendations for User {target_user_id} ---")

    # Get a list of all movie IDs the user has NOT rated
    rated_items = {iid for (iid, _) in trainset.ur[trainset.to_inner_uid(target_user_id)]}
    all_items = set(trainset.all_items())
    unrated_items = all_items - rated_items

    # Predict ratings for the unrated items for both models
    predictions_user = [algo_user.predict(target_user_id, trainset.to_raw_iid(iid)) for iid in unrated_items]
    predictions_item = [algo_item.predict(target_user_id, trainset.to_raw_iid(iid)) for iid in unrated_items]

    # Get the top 10 recommendations from each model's predictions
    top_n_user = get_top_n_recommendations(predictions_user, n=10)
    top_n_item = get_top_n_recommendations(predictions_item, n=10)

    # Print the results
    print("\nTop 10 recommendations from User-Based model:")
    for movie_id, rating in top_n_user[target_user_id]:
        print(f"  - Movie ID: {movie_id}, Predicted Rating: {rating:.2f}")

    print("\nTop 10 recommendations from Item-Based model:")
    for movie_id, rating in top_n_item[target_user_id]:
        print(f"  - Movie ID: {movie_id}, Predicted Rating: {rating:.2f}")

if __name__ == "__main__":
    run_recommendation_system()
