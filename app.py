from flask import Flask, render_template, request, redirect, url_for
from services.allocation import allocate_funds, compute_display_percentages
from db import init_db, list_targets, insert_target, update_target_weight, delete_target
from db import list_transactions, insert_transaction, insert_purchase, list_purchases
from db import clear_targets, get_achieved_keys, clear_achievements
from datetime import datetime, date
from services.weights import normalize_to_100
from achievements import check_and_unlock_achievements, ACHIEVEMENTS



def create_app():
    app = Flask(__name__)
    init_db()


    TOTAL_SAVED = 100.0
    PURCHASES = []


    def compute_total_saved():
        transactions = list_transactions()
        purchases = list_purchases()

        saved = sum(t["amount"] for t in transactions)
        spent = sum(p["amount"] for p in purchases)

        return max(0, saved - spent)






    @app.route("/")
    def home():
        newly_unlocked = check_and_unlock_achievements()
        return render_template(
            "home.html",
            newly_unlocked=newly_unlocked
        )

    @app.route("/targets")
    def targets():
        total_saved = compute_total_saved()
        targets = list_targets()
        allocations = allocate_funds(total_saved, targets)
        return render_template(
            "targets.html",
            total_saved=total_saved,
            targets=allocations,
            editing=False
        )

    @app.route("/transactions", methods=["GET", "POST"])
    def transactions():
        if request.method == "POST":
            date = request.form["date"]
            raw_amount = float(request.form["amount"])
            txn_type = request.form["txn_type"]
            category = request.form["category"]

            amount = raw_amount if txn_type == "save" else -raw_amount

            insert_transaction(
                date=date,
                amount=amount,
                category=category,
                txn_type=txn_type,
            )





            return redirect(url_for("transactions"))

        total_saved = compute_total_saved()
        return render_template(
            "transactions.html",
            transactions=list_transactions(),
            total_saved=compute_total_saved()
        )
    
    @app.route("/targets/update-weight", methods=["POST"])
    def update_weight():
        target_id = request.form.get("target_id")
        new_pct = request.form.get("weight_pct")

        if target_id is None or new_pct is None:
            return redirect(url_for("targets"))

        target_id = int(target_id)
        new_pct = max(0, min(100, int(new_pct)))

        targets = list_targets()

        others = [t for t in targets if t["id"] != target_id]
        other_total = sum(t["weight"] for t in others)

        for t in targets:
            if t["id"] == target_id:
                update_target_weight(t["id"], new_pct)
            else:
                if other_total > 0:
                    redistributed = round(
                        t["weight"] * (100 - new_pct) / other_total
                    )
                    update_target_weight(t["id"], redistributed)
                else:
                    update_target_weight(t["id"], 0)

        return redirect(url_for("targets"))


    
    @app.route("/targets/purchase", methods=["POST"])
    def purchase_target():
        target_id = request.form.get("target_id")

        if not target_id:
            return redirect(url_for("targets"))

        target_id = int(target_id)

        targets = list_targets()
        target = next((t for t in targets if t["id"] == target_id), None)

        if not target:
            return redirect(url_for("targets"))

        insert_purchase(
            target_name=target["name"],
            amount=target["price"],
            purchased_at=datetime.utcnow().isoformat()
        )

        delete_target(target_id)

        insert_transaction(
            date=date.today().isoformat(),
            amount=-target["price"],
            category="Target Purchase",
            txn_type="spend"
        )

        return redirect(url_for("targets"))



    
    @app.route("/targets/add", methods=["POST"])
    def add_target():
        name = request.form["name"]
        price = float(request.form["price"])
        mode = request.form.get("priority_mode")

        # Fetch current targets AFTER last normalization
        targets = list_targets()
        existing_count = len(targets)
        print("DEBUG existing_count:", existing_count)
        print("DEBUG target_ids:", [t["id"] for t in targets])


        # Decide initial weight for new target
        if mode == "manual":
            raw = request.form.get("weight")
            new_weight = int(raw) if raw and raw.isdigit() else 0
        else:
            # DEFAULT MODE:
            # give new item same raw weight as others (equal-share intent)
            if existing_count > 0:
                current_total = sum(t["weight"] for t in targets)
                new_weight = current_total / existing_count
            else:
                new_weight = 100

        # Insert new target
        new_id = insert_target(
            name=name,
            price=price,
            weight=new_weight
        )

        # Re-fetch ALL targets from DB (single source of truth)
        all_targets = list_targets()

        # Build raw list from DB ONLY
        raw_items = [{"id": t["id"], "w": t["weight"]} for t in all_targets]

        # Normalize to 100
        normalized = normalize_to_100(raw_items)

        # Persist normalized weights (overwrite everything)
        for tid, pct in normalized.items():
            update_target_weight(tid, pct)

        return redirect(url_for("targets"))



    
    @app.route("/targets/clear", methods=["POST"])
    def clear_all_targets():
        clear_targets()
        return redirect(url_for("targets"))
    
    @app.route("/targets/edit")
    def edit_targets():
        total_saved = compute_total_saved()
        targets = allocate_funds(total_saved, list_targets())
        return render_template(
            "targets.html",
            total_saved=total_saved,
            targets=targets,
            editing=True
        )


    @app.route("/targets/cancel-edit")
    def cancel_edit_targets():
        return redirect(url_for("targets"))
    
    @app.route("/targets/save-weights", methods=["POST"])
    def save_weights():
        raw = {}

        # 1. Extract submitted weights
        for key, value in request.form.items():
            if key.startswith("weights[") and key.endswith("]"):
                target_id = int(key[8:-1])
                raw_weight = float(value) if value else 0.0
                raw[target_id] = raw_weight

        if not raw:
            return redirect(url_for("targets"))

        # 2. Normalize to 100
        items = [{"id": tid, "w": w} for tid, w in raw.items()]
        normalized = normalize_to_100(items)

        # 3. Persist
        for tid, pct in normalized.items():
            update_target_weight(tid, pct)

        return redirect(url_for("targets"))

    @app.route("/achievements")
    def achievements_page():
        
        achieved_keys = get_achieved_keys()

        return render_template(
            "achievements.html",
            achievements=ACHIEVEMENTS,
            achieved_keys=achieved_keys
        )
    
    @app.route("/achievements/reset", methods=["POST"])
    def reset_achievements():
        clear_achievements()
        return redirect(url_for("achievements_page"))

        
        




    
    return app

