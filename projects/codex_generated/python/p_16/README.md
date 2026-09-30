# Collaborative Filtering Recommender

Generates top-N recommendations using user-based and item-based collaborative filtering with configurable similarity metrics.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Input format

Provide a CSV with columns:

```
user,item,rating
u1,i1,4
u1,i2,5
u2,i1,3
...
```

## Usage

```bash
python recommendation_system.py \
  --ratings ratings.csv \
  --mode both \
  --similarity cosine \
  --neighbors 15 \
  --top-n 5 \
  --output recommendations.csv
```

Options:
- `--mode`: `user`, `item`, or `both` (default combines both approaches).
- `--similarity`: `cosine` or `pearson`.
- `--neighbors`: Number of nearest neighbors to consider (default `20`).
- `--top-n`: Recommendations per user (default `5`).
- `--users`: Space-separated list of user IDs to generate recommendations for; defaults to all.
- `--min-ratings`: Minimum number of ratings required for users/items to be kept.

The script outputs `recommendations.csv` with columns `user,item,score` representing predicted preference scores sorted descending per user.
