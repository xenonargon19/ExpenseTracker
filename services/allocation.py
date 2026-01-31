def allocate_funds(total_saved, targets):
        # Initialize working state
        # Filter out invalid weights
        working = []
        for t in targets:
            if t["weight"] < 0:
                raise ValueError(f"Negative weight not allowed: {t['name']}")

            working.append({
                "id": t["id"],
                "name": t["name"],
                "price": t["price"],
                "weight": t["weight"],
                "allocated": 0.0,
            })

        remaining_money = total_saved
        active = [t for t in working if t["weight"] > 0]

        while remaining_money > 0 and active:
            # Normalize weights implicitly via division by total_weight
            total_weight = sum(t["weight"] for t in active)
            excess = 0.0
            next_active = []

            for t in active:
                share = remaining_money * (t["weight"] / total_weight)
                capacity = t["price"] - t["allocated"]

                if share >= capacity:
                    t["allocated"] += capacity
                    excess += share - capacity
                else:
                    t["allocated"] += share
                    next_active.append(t)

            remaining_money = excess
            active = next_active

        # Prepare output
        result = []
        for t in working:
            progress = min(t["allocated"] / t["price"], 1.0)
            result.append({
                "id": t["id"],
                "name": t["name"],
                "price": t["price"],
                "weight": t["weight"],
                "allocated": round(t["allocated"], 2),
                "progress": round(progress * 100, 1),
            })


        weights = [t["weight"] for t in result]
        display_percents = compute_display_percentages(weights)

        for t, pct in zip(result, display_percents):
            t["display_weight_pct"] = pct

        # Sort by descending weight (higher priority first)
        result.sort(key=lambda x: x["weight"], reverse=True)

        return result

def compute_display_percentages(weights):
    total = sum(weights)
    if total == 0:
        return [0 for _ in weights]

    exact = [(w / total) * 100 for w in weights]
    floored = [int(p) for p in exact]
    remainder = [p - f for p, f in zip(exact, floored)]

    remaining = 100 - sum(floored)

    # Distribute remaining points by largest remainder
    indices = sorted(
        range(len(weights)),
        key=lambda i: remainder[i],
        reverse=True
    )

    for i in indices[:remaining]:
        floored[i] += 1

    return floored
