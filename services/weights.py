def normalize_to_100(items):
    """
    items: list of dicts like [{"id": 1, "w": 20.0}, ...]
    Returns: dict {id: int_weight} that sums to exactly 100
    Uses largest remainder method.
    """
    total = sum(max(0.0, float(x["w"])) for x in items)
    if total <= 0:
        # If everything is 0, return all 0s
        return {x["id"]: 0 for x in items}

    exact = []
    for x in items:
        w = max(0.0, float(x["w"]))
        pct = (w / total) * 100.0
        exact.append((x["id"], pct))

    floored = {i: int(pct) for i, pct in exact}
    remainders = [(i, pct - floored[i]) for i, pct in exact]

    remaining = 100 - sum(floored.values())
    remainders.sort(key=lambda t: t[1], reverse=True)

    for k in range(remaining):
        floored[remainders[k][0]] += 1

    return floored
