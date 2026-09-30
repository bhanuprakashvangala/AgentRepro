#!/usr/bin/env python3
"""Example API client using Redis caching decorators."""

from __future__ import annotations

import os
import random
import time
from typing import Dict

import requests

from redis_cache import cache, invalidate

API_ENDPOINT = "https://api.agify.io"


@cache(ttl=120, namespace="agify")
def get_age_prediction(name: str) -> Dict[str, int]:
    """Fetch age prediction from agify.io with caching."""
    response = requests.get(API_ENDPOINT, params={"name": name}, timeout=5)
    response.raise_for_status()
    return response.json()


def main() -> None:
    names = ["alice", "bob", "charlie", "diana"]
    for _ in range(5):
        name = random.choice(names)
        result = get_age_prediction(name)
        print(f"Prediction for {name}: {result}")
        time.sleep(1)

    # Demonstrate invalidation
    print("Invalidating agify namespace...")
    deleted = invalidate(namespace="agify")
    print(f"Deleted {deleted} keys")

    # Fetch again to show cache miss
    print(get_age_prediction("alice"))


if __name__ == "__main__":
    main()
