import pandas as pd
import pymysql
from pathlib import Path

project_root = Path.cwd().parent
data_dir = project_root / "data"
connection = pymysql.connect(
    host="localhost",
    user="root",
    password= #insert own password!!!,
    database="shanghai_real_estate",
    charset="utf8mb4"
)

cursor = connection.cursor()


def clean(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def district_key(value):
    return str(value).lower().replace("'", "").replace(" ", "").strip()


try:
    buy = pd.read_csv(data_dir / "lianjia_buy_clean_20260606.csv")
    rent = pd.read_csv(data_dir / "lianjia_rent_clean_20260606.csv")
    monthly = pd.read_csv(data_dir / "shanghai_housing_prices.csv")
    annual = pd.read_csv(data_dir / "shanghai_housing_prices_annual.csv")
    income = pd.read_csv(data_dir / "shanghai_income_final.csv")

    # 1. Districts
    for name in monthly["district"].dropna().unique():
        cursor.execute(
            """
            INSERT IGNORE INTO districts (district_key, district_name)
            VALUES (%s, %s)
            """,
            (district_key(name), str(name))
        )

    connection.commit()

    cursor.execute(
        """
        SELECT district_id, district_key
        FROM districts
        """
    )

    districts = {}

    for district_id, key in cursor.fetchall():
        districts[key] = district_id

    buy_sql = """
    INSERT IGNORE INTO buy_listings (
        district_id,
        community,
        title,
        layout,
        bedrooms,
        area_sqm,
        orientation,
        decoration,
        decoration_en,
        floor_level,
        floor_level_en,
        total_floors,
        build_year,
        property_age,
        building_type,
        building_type_en,
        total_price_wan,
        total_price_yuan,
        unit_price_yuan_sqm,
        tags,
        listing_url
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s
    )
    """

    for _, row in buy.iterrows():
        key = district_key(row["district"])

        cursor.execute(
            buy_sql,
            (
                districts[key],
                clean(row["community"]),
                clean(row["title"]),
                clean(row["layout"]),
                clean(row["bedrooms"]),
                clean(row["area_sqm"]),
                clean(row["orientation"]),
                clean(row["decoration"]),
                clean(row["decoration_en"]),
                clean(row["floor_level"]),
                clean(row["floor_level_en"]),
                clean(row["total_floors"]),
                clean(row["build_year"]),
                clean(row["property_age"]),
                clean(row["building_type"]),
                clean(row["building_type_en"]),
                clean(row["total_price_wan"]),
                clean(row["total_price_yuan"]),
                clean(row["unit_price_yuan_sqm"]),
                clean(row["tags"]),
                clean(row["listing_url"])
            )
        )

    connection.commit()
    print("Buy listings loaded")

    rent_sql = """
    INSERT IGNORE INTO rent_listings (
        district_id,
        community,
        title,
        area_sqm,
        layout,
        orientation,
        monthly_rent_yuan,
        rent_per_sqm,
        tags,
        listing_url,
        scraped_date,
        listing_type
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in rent.iterrows():
        key = district_key(row["district"])

        scraped_date = None

        if not pd.isna(row["scraped_date"]):
            scraped_date = pd.to_datetime(
                str(int(row["scraped_date"])),
                format="%Y%m%d"
            ).date()

        cursor.execute(
            rent_sql,
            (
                districts[key],
                clean(row["community"]),
                clean(row["title"]),
                clean(row["area_sqm"]),
                clean(row["layout"]),
                clean(row["orientation"]),
                clean(row["monthly_rent_yuan"]),
                clean(row["rent_per_sqm"]),
                clean(row["tags"]),
                clean(row["listing_url"]),
                scraped_date,
                clean(row["listing_type"])
            )
        )

    connection.commit()
    print("Rent listings loaded")

    monthly_sql = """
    INSERT IGNORE INTO housing_prices_monthly (
        district_id,
        source_district_id,
        price_year,
        price_month,
        price_date,
        price_per_sqm
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for _, row in monthly.iterrows():
        key = district_key(row["district"])
        price_date = pd.to_datetime(row["date"]).date()

        cursor.execute(
            monthly_sql,
            (
                districts[key],
                clean(row["district_id"]),
                int(row["year"]),
                int(row["month"]),
                price_date,
                clean(row["price_per_sqm"])
            )
        )

    connection.commit()
    print("Monthly prices loaded")

    annual_sql = """
    INSERT IGNORE INTO housing_prices_annual (
        district_id,
        source_district_id,
        price_year,
        avg_price_per_sqm
    )
    VALUES (%s, %s, %s, %s)
    """

    for _, row in annual.iterrows():
        key = district_key(row["district"])

        cursor.execute(
            annual_sql,
            (
                districts[key],
                clean(row["district_id"]),
                int(row["year"]),
                clean(row["avg_annual_price_per_sqm"])
            )
        )

    connection.commit()
    print("Annual prices loaded")

    income_sql = """
    INSERT IGNORE INTO city_income_annual (
        income_year,
        city_name,
        source_district_id,
        income_per_capita
    )
    VALUES (%s, %s, %s, %s)
    """

    for _, row in income.iterrows():
        cursor.execute(
            income_sql,
            (
                int(row["year"]),
                clean(row["district"]),
                clean(row["district_id"]),
                clean(row["urban_disposable_income_per_capita"])
            )
        )

    connection.commit()
    print("Income data loaded")

    tables = [
        "districts",
        "buy_listings",
        "rent_listings",
        "housing_prices_monthly",
        "housing_prices_annual",
        "city_income_annual"
    ]

    print("\nRows in database:")

    for table in tables:
        cursor.execute("SELECT COUNT(*) FROM " + table)
        count = cursor.fetchone()[0]
        print(table, count)

except Exception as error:
    connection.rollback()
    print("Error:", error)

finally:
    cursor.close()
    connection.close()
