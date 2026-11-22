"""Full-flow smoke test (PLAN.md section 8, item 2).

Starts the app with TestClient on a throwaway SQLite file, logs in as the demo
user, then exercises the complete vendor flow and asserts the contract.
"""
from __future__ import annotations

import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import create_app  # noqa: E402
from app.rate_limit import login_limiter  # noqa: E402


def fail(message: str) -> None:
    print(f"SMOKE FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    login_limiter.reset()
    with tempfile.TemporaryDirectory() as tmp:
        url = f"sqlite:///{Path(tmp) / 'smoke.db'}"
        app = create_app(database_url=url, seed=True)
        with TestClient(app) as client:
            # Health and login gate.
            health = client.get("/healthz")
            check(health.status_code == 200 and health.json() == {"status": "ok", "db": "ok"},
                  f"/healthz returned {health.status_code} {health.text}")
            check(client.get("/api/businesses").status_code == 401, "API must require login")

            login = client.post(
                "/login", data={"username": "demo", "password": "demo123"}, follow_redirects=False
            )
            check(login.status_code == 303, f"demo login failed: {login.status_code}")

            # Create a business and a product.
            business = client.post(
                "/api/businesses",
                json={
                    "name": "Smoke Warung",
                    "business_type": "warung",
                    "location_type": "kampus",
                    "capacity_factor": 1.0,
                },
            )
            check(business.status_code == 201, f"create business: {business.status_code} {business.text}")
            business_id = business.json()["id"]

            product = client.post(
                f"/api/businesses/{business_id}/products",
                json={"name": "Nasi Smoke", "category": "nasi", "price": 12000, "unit_cost": 5000},
            )
            check(product.status_code == 201, f"create product: {product.status_code} {product.text}")
            product_id = product.json()["id"]

            # Record 3 days of sales -> H3.
            today = date.today()
            for offset in range(3, 0, -1):
                day = (today - timedelta(days=offset)).isoformat()
                response = client.post(
                    "/api/sales",
                    json={"product_id": product_id, "date": day, "qty_sold": 18 + offset, "sold_out": False},
                )
                check(response.status_code == 200, f"post sale {day}: {response.status_code} {response.text}")

            url = f"/api/products/{product_id}/recommendation"
            rec = client.get(url, params={"date": (today + timedelta(days=1)).isoformat()})
            check(rec.status_code == 200, f"recommendation: {rec.status_code} {rec.text}")
            body = rec.json()
            check(body["stage"] == "H3", f"expected H3, got {body['stage']}")
            check(body["n_days"] == 3, f"expected n_days=3, got {body['n_days']}")
            check(isinstance(body["p10"], int) and isinstance(body["p50"], int)
                  and isinstance(body["p90"], int), "quantiles must be ints")
            check(0 <= body["p10"] <= body["p50"] <= body["p90"],
                  f"quantile order broken: {body['p10']},{body['p50']},{body['p90']}")
            check(isinstance(body["recommended_qty"], int) and body["recommended_qty"] >= 0,
                  "recommended_qty must be int >= 0")
            check(body["confidence"] in {"rendah", "sedang", "tinggi"},
                  f"confidence invalid: {body['confidence']}")
            check(bool(body["reasons"]), "reasons must be non-empty")
            check(0.05 <= body["alpha"] <= 0.95, f"alpha out of range: {body['alpha']}")
            print(f"smoke: H3 ok -> p10={body['p10']} p50={body['p50']} p90={body['p90']} "
                  f"qty={body['recommended_qty']} conf={body['confidence']}")

            # Four more days -> H7.
            for offset in range(7, 3, -1):
                day = (today - timedelta(days=offset)).isoformat()
                response = client.post(
                    "/api/sales",
                    json={"product_id": product_id, "date": day, "qty_sold": 20, "sold_out": offset == 4},
                )
                check(response.status_code == 200, f"post sale {day}: {response.status_code}")
            rec7 = client.get(url, params={"date": (today + timedelta(days=1)).isoformat()}).json()
            check(rec7["stage"] == "H7", f"expected H7, got {rec7['stage']}")
            check(rec7["n_days"] == 7, f"expected n_days=7, got {rec7['n_days']}")
            check(rec7["p10"] <= rec7["p50"] <= rec7["p90"], "H7 quantile order broken")
            check(rec7["confidence"] in {"rendah", "sedang", "tinggi"}, "H7 confidence invalid")
            print(f"smoke: H7 ok -> qty={rec7['recommended_qty']} conf={rec7['confidence']}")

            # Seeded demo shows all three stages, and the dashboard renders.
            stages = set()
            for seeded in client.get("/api/businesses").json():
                if seeded["name"] == "Smoke Warung":
                    continue
                items = client.get(f"/api/businesses/{seeded['id']}/recommendations").json()["items"]
                stages.update(item["stage"] for item in items)
            check({"H0", "H3", "H7"} <= stages, f"seeded stages incomplete: {sorted(stages)}")
            dashboard = client.get(f"/?business_id={business_id}")
            check(dashboard.status_code == 200, "dashboard failed to render")
            check('id="recommendation-grid"' in dashboard.text, "dashboard grid missing")
            for path in ("/business", "/sales/new", "/sales", "/import"):
                check(client.get(path).status_code == 200, f"page {path} failed")

            # CSV import path.
            csv_body = (
                "date,product,qty_sold,sold_out\n"
                f"{(today - timedelta(days=8)).isoformat()},Nasi Smoke,21,false\n"
            )
            imported = client.post(
                f"/api/businesses/{business_id}/sales/import",
                files={"file": ("smoke.csv", csv_body.encode(), "text/csv")},
            )
            check(imported.status_code == 200 and imported.json()["accepted"] == 1,
                  f"CSV import failed: {imported.status_code} {imported.text}")
            print("smoke: CSV import ok")

    print("smoke: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
