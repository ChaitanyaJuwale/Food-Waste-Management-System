--Food Providers & Receivers
--1. How many food providers and receivers are there in each city?
SELECT city,
       COUNT(DISTINCT provider_id) AS total_providers,
       COUNT(DISTINCT receiver_id) AS total_receivers
FROM (
    SELECT city, provider_id, NULL::INT AS receiver_id FROM providers
    UNION ALL
    SELECT city, NULL::INT AS provider_id, receiver_id FROM receivers
) AS combined
GROUP BY city
ORDER BY city;

--2. Which type of food provider contributes the most food?
SELECT p.type AS provider_type, SUM(f.quantity) AS total_quantity
FROM food_listings f
JOIN providers p ON f.provider_id = p.provider_id
GROUP BY p.type
ORDER BY total_quantity DESC
LIMIT 1;

--3. Contact info of food providers in a specific city (example for New Carol):
SELECT name, type, address, contact
FROM providers
WHERE city = 'New Carol'
ORDER BY name;

--4. Which receivers have claimed the most food?
SELECT r.name AS receiver, COUNT(c.claim_id) AS total_claims
FROM claims c
JOIN receivers r ON c.receiver_id = r.receiver_id
GROUP BY r.name
ORDER BY total_claims DESC
LIMIT 10;

--Food Listings & Availability
--5. Total quantity of food available from all providers
SELECT SUM(quantity) AS total_quantity_available
FROM food_listings;

--6. Which city has the highest number of food listings?
SELECT p.city, COUNT(f.food_id) AS total_listings
FROM food_listings f
JOIN providers p ON f.provider_id = p.provider_id
GROUP BY p.city
ORDER BY total_listings DESC
LIMIT 1;

--7. Most commonly available food types
SELECT food_type, COUNT(*) AS count
FROM food_listings
GROUP BY food_type
ORDER BY count DESC;

--Claims & Distribution
--8. How many food claims have been made for each food item?
SELECT f.food_name, COUNT(c.claim_id) AS total_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY f.food_name
ORDER BY total_claims DESC;

--9. Which provider has the highest number of successful claims?
SELECT p.name AS provider, COUNT(c.claim_id) AS successful_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
JOIN providers p ON f.provider_id = p.provider_id
WHERE c.status = 'Completed'
GROUP BY p.name
ORDER BY successful_claims DESC
LIMIT 1;

--10. Percentage of claims by status
SELECT status, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS percentage
FROM claims
GROUP BY status;

--Analysis & Insights
--11. Average quantity of food claimed per receiver
SELECT r.name AS receiver, ROUND(AVG(f.quantity), 2) AS avg_quantity_claimed
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
JOIN receivers r ON c.receiver_id = r.receiver_id
GROUP BY r.name
ORDER BY avg_quantity_claimed DESC;

--12. Which meal type is claimed the most?
SELECT f.meal_type, COUNT(*) AS total_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
GROUP BY f.meal_type
ORDER BY total_claims DESC;

--13. Total quantity donated by each provider
SELECT p.name AS provider, SUM(f.quantity) AS total_quantity
FROM food_listings f
JOIN providers p ON f.provider_id = p.provider_id
GROUP BY p.name
ORDER BY total_quantity DESC;

--Additional Queries
--14. Top 5 cities with most claims
SELECT p.city, COUNT(c.claim_id) AS total_claims
FROM claims c
JOIN food_listings f ON c.food_id = f.food_id
JOIN providers p ON f.provider_id = p.provider_id
GROUP BY p.city
ORDER BY total_claims DESC
LIMIT 5;

--15. Providers who never had their food claimed
SELECT p.name AS provider
FROM providers p
LEFT JOIN food_listings f ON p.provider_id = f.provider_id
LEFT JOIN claims c ON f.food_id = c.food_id
WHERE c.claim_id IS NULL;


