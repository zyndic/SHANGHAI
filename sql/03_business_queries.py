
import pymysql


connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Nastya2805",
    database="shanghai_real_estate",
    charset="utf8mb4"
)

cursor = connection.cursor()


def find_district_id():
    district_name = input("District name: ").lower()
    district_name = district_name.replace("'", "").replace(" ", "")

    cursor.execute(
        """
        SELECT district_id
        FROM districts
        WHERE district_key = %s
        """,
        (district_name,)
    )

    result = cursor.fetchone()

    if result is None:
        print("District was not found")
        return None

    return result[0]


def show_rows(rows):
    print("Rows found:", len(rows))

    if len(rows) == 0:
        print("No data found")
        return

    for row in rows[:20]:
        print(row)

    if len(rows) > 20:
        print("Only the first 20 rows are shown")


while True:
    print("\n1 - Show all districts")
    print("2 - Find sale listings")
    print("3 - Find rental listings")
    print("4 - Find rental listings near metro")
    print("5 - Search by community name")
    print("6 - Show annual prices")
    print("7 - Show monthly prices")
    print("8 - Show city income")
    print("9 - Find a listing by URL")
    print("0 - Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        cursor.execute(
            """
            SELECT district_id, district_name
            FROM districts
            """
        )

        show_rows(cursor.fetchall())

    elif choice == "2":
        district_id = find_district_id()

        if district_id is None:
            continue

        bedrooms = int(input("Number of bedrooms: "))
        min_area = float(input("Minimum area: "))
        max_price = float(input("Maximum total price: "))

        cursor.execute(
            """
            SELECT
                buy_id,
                community,
                title,
                bedrooms,
                area_sqm,
                total_price_yuan,
                unit_price_yuan_sqm,
                listing_url
            FROM buy_listings
            WHERE district_id = %s
              AND bedrooms = %s
              AND area_sqm >= %s
              AND total_price_yuan <= %s
            """,
            (
                district_id,
                bedrooms,
                min_area,
                max_price
            )
        )

        show_rows(cursor.fetchall())

    elif choice == "3":
        district_id = find_district_id()

        if district_id is None:
            continue

        min_area = float(input("Minimum area: "))
        max_rent = float(input("Maximum monthly rent: "))

        cursor.execute(
            """
            SELECT
                rent_id,
                community,
                title,
                area_sqm,
                layout,
                monthly_rent_yuan,
                rent_per_sqm,
                tags,
                listing_url
            FROM rent_listings
            WHERE district_id = %s
              AND area_sqm >= %s
              AND monthly_rent_yuan <= %s
            """,
            (
                district_id,
                min_area,
                max_rent
            )
        )

        show_rows(cursor.fetchall())

    elif choice == "4":
        district_id = find_district_id()

        if district_id is None:
            continue

        min_area = float(input("Minimum area: "))
        max_rent = float(input("Maximum monthly rent: "))

        cursor.execute(
            """
            SELECT
                rent_id,
                community,
                title,
                area_sqm,
                layout,
                monthly_rent_yuan,
                rent_per_sqm,
                tags,
                listing_url
            FROM rent_listings
            WHERE district_id = %s
              AND area_sqm >= %s
              AND monthly_rent_yuan <= %s
              AND tags LIKE %s
            """,
            (
                district_id,
                min_area,
                max_rent,
                "%近地铁%"
            )
        )

        show_rows(cursor.fetchall())

    elif choice == "5":
        community_name = input("Community name or part of name: ")

        cursor.execute(
            """
            SELECT
                rent_id,
                community,
                title,
                area_sqm,
                monthly_rent_yuan,
                listing_url
            FROM rent_listings
            WHERE community LIKE %s
            """,
            ("%" + community_name + "%",)
        )

        show_rows(cursor.fetchall())

    elif choice == "6":
        district_id = find_district_id()

        if district_id is None:
            continue

        cursor.execute(
            """
            SELECT
                price_year,
                avg_price_per_sqm
            FROM housing_prices_annual
            WHERE district_id = %s
            """,
            (district_id,)
        )

        show_rows(cursor.fetchall())

    elif choice == "7":
        district_id = find_district_id()

        if district_id is None:
            continue

        year = int(input("Year: "))

        cursor.execute(
            """
            SELECT
                price_year,
                price_month,
                price_date,
                price_per_sqm
            FROM housing_prices_monthly
            WHERE district_id = %s
              AND price_year = %s
            """,
            (
                district_id,
                year
            )
        )

        show_rows(cursor.fetchall())

    elif choice == "8":
        year = int(input("Year: "))

        cursor.execute(
            """
            SELECT
                income_year,
                city_name,
                income_per_capita
            FROM city_income_annual
            WHERE income_year = %s
            """,
            (year,)
        )

        result = cursor.fetchone()

        if result is None:
            print("No data found")
        else:
            print(result)

    elif choice == "9":
        listing_url = input("Listing URL: ")

        cursor.execute(
            """
            SELECT
                buy_id,
                community,
                title,
                area_sqm,
                total_price_yuan,
                listing_url
            FROM buy_listings
            WHERE listing_url = %s
            """,
            (listing_url,)
        )

        result = cursor.fetchone()

        if result is None:
            cursor.execute(
                """
                SELECT
                    rent_id,
                    community,
                    title,
                    area_sqm,
                    monthly_rent_yuan,
                    listing_url
                FROM rent_listings
                WHERE listing_url = %s
                """,
                (listing_url,)
            )

            result = cursor.fetchone()

        if result is None:
            print("Listing was not found")
        else:
            print(result)

    elif choice == "0":
        break

    else:
        print("Unknown option")


cursor.close()
connection.close()
