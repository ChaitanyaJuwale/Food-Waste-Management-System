
--Back up first
CREATE TABLE IF NOT EXISTS backup_food_listings AS TABLE food_listings;

--obvious mislabels (veg-looking names marked Non-Veg):
SELECT food_id, food_name, food_type
FROM food_listings
WHERE food_type = 'Non-Vegetarian'
  AND food_name ~* '(bread|roti|chapati|paratha|rice|dal|chana|chhole|rajma|paneer|tofu|veg|vegetable|salad|fruit|banana|apple|poha|upma|idli|dosa|sambar)';

--similarly there are mistakes for vegan and vegetarian food type

--Unique food Names
SELECT DISTINCT food_name
FROM food_listings
ORDER BY food_name;

-- Unique food_type
SELECT DISTINCT food_type
FROM food_listings
ORDER BY food_type;

--Update Query
UPDATE food_listings
SET food_type = CASE
    WHEN food_name ILIKE 'Chicken' THEN 'Non-Vegetarian'
    WHEN food_name ILIKE 'Fish' THEN 'Non-Vegetarian'
    WHEN food_name ILIKE 'Dairy' THEN 'Vegetarian'
    WHEN food_name ILIKE ANY(ARRAY['Bread','Fruits','Pasta','Rice','Salad','Soup','Vegetables']) THEN 'Vegan'
    ELSE food_type
END
WHERE food_name ILIKE ANY(ARRAY['Bread','Chicken','Dairy','Fish','Fruits','Pasta','Rice','Salad','Soup','Vegetables']);

--Verify the Update
SELECT food_name, food_type
FROM food_listings
WHERE food_name ILIKE ANY(ARRAY['Bread','Chicken','Dairy','Fish','Fruits','Pasta','Rice','Salad','Soup','Vegetables'])
ORDER BY food_name;

--Audit what changed
SELECT f.food_id, f.food_name, f.food_type
FROM food_listings f
JOIN backup_food_listings b USING(food_id)
WHERE f.food_type IS DISTINCT FROM b.food_type
ORDER BY f.food_id;

--Updated Number of food items by name
SELECT food_name, COUNT(*) AS item_count
FROM food_listings
GROUP BY food_name
ORDER BY item_count DESC;

--Updated Number of food items by type
SELECT food_type, COUNT(*) AS type_count
FROM food_listings
GROUP BY food_type
ORDER BY type_count DESC;
