
SELECT member_id,
    sum(b.total_items_price) spending
FROM orders a
    LEFT JOIN order_items b ON a.id = b.order_id
    INNER JOIN members c ON a.member_id = c.id
GROUP BY member_id
ORDER BY spending DESC
LIMIT 10