"""
Genera dashboard.html (pagina autonoma, lista para GitHub Pages) a partir de ventas_envios.csv.

Uso:
    pip install pandas
    python build_dashboard.py
"""
import json
from pathlib import Path

import pandas as pd

df = pd.read_csv(
    "ventas_envios.csv",
    parse_dates=["order_created_date", "delivery_date"],
)
df["ym"] = df["order_created_date"].dt.strftime("%Y-%m")
df["dd"] = (df["delivery_date"] - df["order_created_date"]).dt.days.fillna(-1).astype(int)
df["rt"] = df["customer_rating"].fillna(0).astype(int)

months = sorted(df["ym"].unique())
countries = sorted(df["country"].unique())
categories = (
    df[~df["order_status"].isin(["Cancelado", "Devuelto"])]
    .groupby("category")["total_amount"].sum().sort_values(ascending=False).index.tolist()
)
channels = sorted(df["channel_group"].unique())
methods = sorted(df["shipping_method"].unique())
statuses = sorted(df["order_status"].unique())

idx = lambda col, lst: df[col].map({v: i for i, v in enumerate(lst)}).astype(int)
orders = pd.factorize(df["order_null"])[0]
custs = pd.factorize(df["customer_id"])[0]

rows = list(zip(
    idx("ym", months), idx("country", countries), idx("category", categories),
    idx("channel_group", channels), idx("shipping_method", methods), idx("order_status", statuses),
    df["total_amount"].round(2), df["quantity"], orders, custs,
    df["dd"], df["rt"], df["is_returned"].astype(int),
))
data = {
    "months": months, "countries": countries, "categories": categories,
    "channels": channels, "methods": methods, "statuses": statuses,
    "rows": [[float(v) if isinstance(v, float) else int(v) for v in r] for r in rows],
}
payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

tpl = Path("dashboard_template.html").read_text(encoding="utf-8").replace("/*DATA*/", payload)
head, body = tpl.split("<!--/head-->")

# Version para publicar como artefacto (sin doctype/html/head/body: la plataforma los agrega)
Path("dashboard_artifact.html").write_text(tpl.replace("<!--/head-->", ""), encoding="utf-8")

# Version autonoma para GitHub Pages u otro hosting
standalone = (
    '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    f"{head}</head>\n<body>\n{body}\n</body>\n</html>\n"
)
Path("dashboard.html").write_text(standalone, encoding="utf-8")
print(f"dashboard.html listo ({len(standalone) / 1024:.0f} KB)")
