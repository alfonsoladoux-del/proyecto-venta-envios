"""
Carga ventas_envios.csv en una base SQLite y ejecuta consultas.sql

Uso:
    python cargar_sqlite.py              # crea ventas.db y muestra el resultado de cada consulta
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

CSV = Path("ventas_envios.csv")
DB = Path("ventas.db")
SQL = Path("consultas.sql")

df = pd.read_csv(CSV)
for col in ["is_sustainable_product", "is_elevated_product", "is_returned"]:
    df[col] = df[col].astype(int)  # SQLite guarda booleanos como 0/1

with sqlite3.connect(DB) as con:
    df.to_sql("ventas", con, if_exists="replace", index=False)
    print(f"Tabla 'ventas' creada: {len(df)} filas\n")

    # Cada consulta empieza con un comentario "-- Q<n>: titulo" y termina en ";"
    texto = SQL.read_text(encoding="utf-8")
    for bloque in re.split(r"(?=^-- Q\d+:)", texto, flags=re.M):
        if not bloque.strip().startswith("-- Q"):
            continue
        titulo = bloque.splitlines()[0].lstrip("- ").strip()
        res = pd.read_sql_query(bloque, con)
        print(titulo)
        print(res.head(12).to_string(index=False), "\n")
