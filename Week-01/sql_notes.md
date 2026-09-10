# Week 1 SQL Notes

## Topics Studied
1. SELECT + WHERE
2. ORDER BY + LIMIT
3. INNER JOIN
4. LEFT JOIN
5. NULL Handling
6. Aggregation (GROUP BY, COUNT, SUM, AVG)
7. Subqueries

## 3 Queries From Memory

### Q1: Find all customers from USA
```sql
SELECT * FROM customers WHERE country = 'USA';
```

### Q2: Find customers who placed orders
```sql
SELECT c.name, o.order_id 
FROM customers c 
JOIN orders o ON c.customer_id = o.customer_id;
```

### Q3: Find customers who never placed orders
```sql
SELECT c.name 
FROM customers c 
LEFT JOIN orders o ON c.customer_id = o.customer_id 
WHERE o.order_id IS NULL;
```

### I have finished the concepts like: 
1. Joins - Inner join, Left join, Right join, Full outer join
2. Aggregation - COUNT, SUM, AVG, MIN, MAX
3. Group By Clause.