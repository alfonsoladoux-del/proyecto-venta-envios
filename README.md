# Análisis de ventas y envíos de un e-commerce

Proyecto de análisis de datos de punta a punta: limpieza y control de calidad, métricas de negocio en Python y SQL, y un dashboard interactivo. Trabaja sobre 5.000 registros de ventas y envíos de 6 países, de enero de 2025 a octubre de 2026.

> **Sobre los datos:** la base es sintética (la genera `generar_datos.py` con semilla fija; solo los `cart_id` cambian en cada ejecución) y los montos están en una escala común, sin conversión entre monedas. El objetivo es mostrar el método de análisis. Las conclusiones describen esta base y no un negocio real.

**Dashboard interactivo:** [ver el panel en línea](https://alfonsoladoux-del.github.io/proyecto-venta-envios/dashboard.html)

## Preguntas de negocio

1. ¿Cuánto se vende, a qué ticket y cómo evoluciona mes a mes?
2. ¿Qué categorías, países y canales concentran el ingreso?
3. ¿Dónde hay más devoluciones y cancelaciones?
4. ¿Cómo rinde la logística según método de envío y transportista?
5. ¿Los descuentos y los productos sostenibles cambian el comportamiento de compra?
6. ¿Cuántos clientes vuelven a comprar?

## Contenido del repositorio

| Archivo | Qué hace |
|---|---|
| `ventas_envios.csv` | Base de datos: 5.000 filas, 33 columnas |
| `generar_datos.py` | Genera la base sintética (semilla fija) |
| `analisis_ventas.py` | Limpieza, control de calidad, KPIs, tablas y gráficos con pandas y matplotlib |
| `cargar_sqlite.py` + `consultas.sql` | Carga la base en SQLite y ejecuta 10 consultas |
| `build_dashboard.py` + `dashboard_template.html` | Construyen `dashboard.html` a partir de la base |
| `dashboard.html` | Dashboard interactivo y autónomo |
| `resultados/` | Tablas CSV, `resumen.json` y gráficos PNG generados por el análisis |

## Cómo ejecutarlo

```bash
pip install -r requirements.txt

python generar_datos.py      # opcional: regenera ventas_envios.csv
python analisis_ventas.py    # tablas y gráficos en ./resultados
python cargar_sqlite.py      # crea ventas.db y muestra el resultado de las 10 consultas
python build_dashboard.py    # regenera dashboard.html
```

## Metodología

- **Calidad de datos:** sin claves duplicadas, sin montos negativos y sin entregas anteriores al envío. Los nulos en `ship_date`, `delivery_date` y `customer_rating` son esperables: corresponden a pedidos cancelados, en preparación o sin calificación.
- **Ingreso neto:** suma de `total_amount` de los pedidos que no están cancelados ni devueltos.
- **Ticket promedio:** ingreso neto dividido por los pedidos con venta neta.
- **Tasas de devolución y cancelación:** porcentaje de ítems devueltos o cancelados.
- **Días de entrega:** días entre `order_created_date` y `delivery_date`.
- **Clientes recurrentes:** clientes con más de un pedido con venta neta.
- Los números del script de Python y los de SQL se contrastaron entre sí (ingreso neto, pedidos, clientes y tasas coinciden).

## Resultados principales

| Indicador | Valor |
|---|---|
| Ingreso neto | 3,90 M |
| Pedidos / clientes | 2.993 / 1.625 |
| Ticket promedio | 1.477 |
| Tasa de devolución | 5,4 % |
| Tasa de cancelación | 6,5 % |
| Entrega promedio | 6,2 días |
| Clientes recurrentes | 48 % |

![Ingreso mensual](resultados/01_ingreso_mensual.png)

### Hallazgos

1. **Electrónica sostiene el negocio.** Aporta el 41,4 % del ingreso neto y su ticket (1.938) es más del doble que el de cualquier otra categoría.
2. **Afiliados vende caro y devuelve más.** Es el 7 % del ingreso, con el ticket más alto (1.724) y la mayor tasa de devolución: 9,2 % contra 5,4 % del total.
3. **"Mismo día" no llega el mismo día.** Tarda 2,0 días desde el pedido porque este espera en promedio 1,5 días hasta liberarse, y tiene la devolución más alta (8,8 %). El método Estándar tarda 8,1 días.
4. **Argentina concentra el 35,1 % del ingreso.** Chile tiene la mayor cancelación (8,5 %) y España el mayor ticket (1.815) con 7,3 % de devolución.
5. **El descuento no mueve unidades.** Los ítems con 30 % de descuento llevan 1,65 unidades en promedio, contra 1,67 sin descuento.
6. **Casi la mitad de los clientes recompra,** y el ingreso mensual oscila entre 125 mil y 211 mil sin una tendencia sostenida.

### Recomendaciones

- Reducir la dependencia de Electrónica sumando oferta en categorías de ticket medio como Deportes e Indumentaria.
- Auditar los productos que se promocionan por Afiliados para entender por qué se devuelven más.
- Medir cuánto tarda cada pedido en liberarse y revisar la promesa de "Mismo día" mientras no se acorte ese tiempo.
- Probar descuentos más bajos o condicionados a un monto mínimo, ya que los actuales no aumentan el volumen en esta base.

## Limitaciones

- Con 5.000 ítems, diferencias de uno o dos puntos porcentuales entre grupos pequeños pueden ser ruido. Los hallazgos son hipótesis para validar, no conclusiones definitivas.
- Los montos no se convirtieron entre monedas porque la base sintética usa una escala común.
- `order_created_date` no incluye la hora, por lo que los tiempos se miden en días.
- Octubre de 2026 está incompleto (llega hasta el día 14) y el gráfico lo marca.

## Habilidades que demuestra

Python (pandas, matplotlib), SQL (CTE, funciones de ventana `LAG`, `RANK`, `ROW_NUMBER`), control de calidad de datos, definición de métricas de negocio, visualización de datos y comunicación de resultados.
