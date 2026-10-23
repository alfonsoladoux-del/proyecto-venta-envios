-- Consultas SQL para el proyecto de ventas y envios (SQLite).
-- Tabla: ventas (una fila por producto dentro de un pedido).
-- Venta neta = pedidos que no estan Cancelados ni Devueltos.

-- Q1: KPIs generales
SELECT
    ROUND(SUM(CASE WHEN order_status NOT IN ('Cancelado','Devuelto') THEN total_amount END), 0) AS ingreso_neto,
    COUNT(DISTINCT order_null)                                                                  AS pedidos,
    COUNT(DISTINCT customer_id)                                                                 AS clientes,
    ROUND(100.0 * AVG(is_returned), 2)                                                          AS tasa_devolucion_pct,
    ROUND(100.0 * AVG(order_status = 'Cancelado'), 2)                                           AS tasa_cancelacion_pct
FROM ventas;

-- Q2: Ingreso neto y ticket promedio por categoria
SELECT
    category,
    ROUND(SUM(total_amount), 0)                                   AS ingreso_neto,
    COUNT(DISTINCT order_null)                                    AS pedidos,
    ROUND(SUM(total_amount) / COUNT(DISTINCT order_null), 0)      AS ticket_promedio,
    ROUND(100.0 * SUM(total_amount) / SUM(SUM(total_amount)) OVER (), 1) AS pct_del_total
FROM ventas
WHERE order_status NOT IN ('Cancelado','Devuelto')
GROUP BY category
ORDER BY ingreso_neto DESC;

-- Q3: Evolucion mensual con variacion contra el mes anterior (window function LAG)
WITH mensual AS (
    SELECT
        SUBSTR(order_created_date, 1, 7) AS mes,
        SUM(total_amount)                AS ingreso
    FROM ventas
    WHERE order_status NOT IN ('Cancelado','Devuelto')
    GROUP BY mes
)
SELECT
    mes,
    ROUND(ingreso, 0) AS ingreso,
    ROUND(100.0 * (ingreso - LAG(ingreso) OVER (ORDER BY mes)) / LAG(ingreso) OVER (ORDER BY mes), 1) AS var_vs_mes_anterior_pct
FROM mensual
ORDER BY mes;

-- Q4: Ranking de canales por ingreso, con tasa de devolucion y cancelacion
SELECT
    channel_group,
    ROUND(SUM(CASE WHEN order_status NOT IN ('Cancelado','Devuelto') THEN total_amount END), 0) AS ingreso_neto,
    RANK() OVER (ORDER BY SUM(CASE WHEN order_status NOT IN ('Cancelado','Devuelto') THEN total_amount END) DESC) AS ranking,
    ROUND(100.0 * AVG(is_returned), 2)                AS devolucion_pct,
    ROUND(100.0 * AVG(order_status = 'Cancelado'), 2) AS cancelacion_pct
FROM ventas
GROUP BY channel_group
ORDER BY ranking;

-- Q5: Mejor subcategoria dentro de cada categoria (ROW_NUMBER + CTE)
WITH sub AS (
    SELECT category, subcategory, SUM(total_amount) AS ingreso
    FROM ventas
    WHERE order_status NOT IN ('Cancelado','Devuelto')
    GROUP BY category, subcategory
),
ordenadas AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY ingreso DESC) AS pos
    FROM sub
)
SELECT category, subcategory, ROUND(ingreso, 0) AS ingreso
FROM ordenadas
WHERE pos = 1
ORDER BY ingreso DESC;

-- Q6: Dias de entrega por pais y metodo de envio (solo pedidos entregados)
SELECT
    country,
    shipping_method,
    COUNT(*) AS items_entregados,
    ROUND(AVG(JULIANDAY(delivery_date) - JULIANDAY(order_created_date)), 1) AS dias_entrega_prom
FROM ventas
WHERE order_status = 'Entregado'
GROUP BY country, shipping_method
ORDER BY country, dias_entrega_prom;

-- Q7: Clientes recurrentes: cuantos pedidos con venta neta hizo cada cliente
WITH pedidos_cliente AS (
    SELECT customer_id, COUNT(DISTINCT order_null) AS pedidos
    FROM ventas
    WHERE order_status NOT IN ('Cancelado','Devuelto')
    GROUP BY customer_id
)
SELECT
    CASE WHEN pedidos = 1 THEN '1 pedido'
         WHEN pedidos = 2 THEN '2 pedidos'
         ELSE '3 o mas pedidos' END AS segmento,
    COUNT(*)                                          AS clientes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_clientes
FROM pedidos_cliente
GROUP BY segmento
ORDER BY MIN(pedidos);

-- Q8: Efecto del descuento en unidades por item y devoluciones
SELECT
    CASE WHEN discount_pct = 0  THEN '0%'
         WHEN discount_pct <= 10 THEN '5-10%'
         WHEN discount_pct <= 20 THEN '15-20%'
         ELSE '30%' END                       AS rango_descuento,
    COUNT(*)                                  AS items,
    ROUND(AVG(quantity), 2)                   AS unidades_por_item,
    ROUND(100.0 * AVG(is_returned), 2)        AS devolucion_pct
FROM ventas
GROUP BY rango_descuento
ORDER BY MIN(discount_pct);

-- Q9: Productos sostenibles vs no sostenibles
SELECT
    CASE WHEN is_sustainable_product = 1 THEN 'Sostenible' ELSE 'No sostenible' END AS tipo,
    COUNT(DISTINCT product_id)                       AS productos,
    ROUND(SUM(total_amount), 0)                      AS ingreso_neto,
    ROUND(100.0 * SUM(total_amount) / SUM(SUM(total_amount)) OVER (), 1) AS pct_ingreso,
    ROUND(AVG(unit_price), 0)                        AS precio_unitario_prom
FROM ventas
WHERE order_status NOT IN ('Cancelado','Devuelto')
GROUP BY is_sustainable_product;

-- Q10: Top 10 productos por ingreso neto
SELECT
    product_name,
    category,
    SUM(quantity)               AS unidades,
    ROUND(SUM(total_amount), 0) AS ingreso_neto
FROM ventas
WHERE order_status NOT IN ('Cancelado','Devuelto')
GROUP BY product_id, product_name, category
ORDER BY ingreso_neto DESC
LIMIT 10;
