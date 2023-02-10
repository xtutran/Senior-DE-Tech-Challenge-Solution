
SELECT item_id, count(distinct order_id) as nb_orders
FROM order_items
GROUP BY item_id
ORDER BY nb_orders DESC
LIMIT 3