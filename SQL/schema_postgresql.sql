-- Providers
CREATE TABLE providers (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
	address VARCHAR(100) NOT NULL,
	city VARCHAR(100) NOT NULL,
    contact VARCHAR(100)
);

-- Receivers
CREATE TABLE receivers (
    receiver_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    contact VARCHAR(100)
);

-- Food Listings
CREATE TABLE food_listings (
    food_id SERIAL PRIMARY KEY,
    food_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    expiry_date DATE NOT NULL,
    provider_id INT NOT NULL REFERENCES providers(provider_id) ON DELETE CASCADE,
    provider_type VARCHAR(100),
    location VARCHAR(100),
    food_type VARCHAR(50) NOT NULL,
    meal_type VARCHAR(50) NOT NULL
);

-- Claims
CREATE TABLE claims (
    claim_id SERIAL PRIMARY KEY,
    food_id INT NOT NULL REFERENCES food_listings(food_id) ON DELETE CASCADE,
    receiver_id INT NOT NULL REFERENCES receivers(receiver_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
