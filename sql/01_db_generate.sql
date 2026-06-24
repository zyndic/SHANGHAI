CREATE DATABASE IF NOT EXISTS shanghai_real_estate
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE shanghai_real_estate;

CREATE TABLE IF NOT EXISTS districts (
    district_id INT AUTO_INCREMENT PRIMARY KEY,
    district_key VARCHAR(50) NOT NULL UNIQUE,
    district_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS buy_listings (
    buy_id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    community VARCHAR(255),
    title TEXT,
    layout VARCHAR(50),
    bedrooms INT,
    area_sqm DECIMAL(10,2),
    orientation VARCHAR(100),
    decoration VARCHAR(100),
    decoration_en VARCHAR(100),
    floor_level VARCHAR(50),
    floor_level_en VARCHAR(50),
    total_floors INT,
    build_year INT,
    property_age INT,
    building_type VARCHAR(100),
    building_type_en VARCHAR(100),
    total_price_wan DECIMAL(12,2),
    total_price_yuan DECIMAL(15,2),
    unit_price_yuan_sqm DECIMAL(12,2),
    tags TEXT,
    listing_url VARCHAR(500) NOT NULL UNIQUE,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE IF NOT EXISTS rent_listings (
    rent_id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    community VARCHAR(255),
    title TEXT,
    area_sqm DECIMAL(10,2),
    layout VARCHAR(50),
    orientation VARCHAR(100),
    monthly_rent_yuan DECIMAL(12,2),
    rent_per_sqm DECIMAL(10,2),
    tags TEXT,
    listing_url VARCHAR(500) NOT NULL UNIQUE,
    scraped_date DATE,
    listing_type VARCHAR(30),
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE IF NOT EXISTS housing_prices_monthly (
    monthly_id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    source_district_id INT,
    price_year INT NOT NULL,
    price_month INT NOT NULL,
    price_date DATE NOT NULL,
    price_per_sqm DECIMAL(12,2),
    UNIQUE (district_id, price_year, price_month),
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE IF NOT EXISTS housing_prices_annual (
    annual_id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    source_district_id INT,
    price_year INT NOT NULL,
    avg_price_per_sqm DECIMAL(12,2),
    UNIQUE (district_id, price_year),
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE IF NOT EXISTS city_income_annual (
    income_year INT PRIMARY KEY,
    city_name VARCHAR(100),
    source_district_id INT,
    income_per_capita DECIMAL(12,2)
);

DESCRIBE districts;
DESCRIBE buy_listings;
DESCRIBE rent_listings;
DESCRIBE housing_prices_monthly;
DESCRIBE housing_prices_annual;
DESCRIBE city_income_annual;

