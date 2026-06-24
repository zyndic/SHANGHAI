import requests
from lxml import etree
from urllib.parse import urljoin
import csv
import time
import re
import os
from pathlib import Path


project_root = Path.cwd().parent
data_folder = project_root / 'data' / 'district'

headers = {
    "User-Agent": "Mozilla/5.0"
}

start_url = "https://fangjia.gotohui.com/fjdata-2500"

output_folder = "shanghai_district_history_price_2023_2026"
os.makedirs(output_folder, exist_ok=True)

district_name_en = {
    "黄浦区": "huangpu",
    "徐汇区": "xuhui",
    "静安区": "jingan",
    "长宁区": "changning",
    "虹口区": "hongkou",
    "浦东新区": "pudong_new_area",
    "杨浦区": "yangpu",
    "普陀区": "putuo",
    "闵行区": "minhang",
    "青浦区": "qingpu",
    "宝山区": "baoshan",
    "嘉定区": "jiading",
    "松江区": "songjiang",
    "金山区": "jinshan",
    "奉贤区": "fengxian",
    "崇明区": "chongming"
}

def clean_text(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_html(url):
    response = requests.get(url, headers=headers, timeout=15)
    response.encoding = response.apparent_encoding
    return etree.HTML(response.text)

def get_district_links(start_url):
    html = get_html(start_url)

    district_links = []
    links = html.xpath('//a[contains(@href, "fjdata-")]')

    for link in links:
        name = clean_text("".join(link.xpath(".//text()")))
        href_list = link.xpath("./@href")

        if not href_list:
            continue

        href = href_list[0]
        full_url = urljoin(start_url, href)

       # Keep only Shanghai district-level links and exclude non-specific areas such as "市区"
        if name.endswith("区") and name != "市区" and "上海" not in name:
            district_id_match = re.search(r"fjdata-(\d+)", full_url)

            if district_id_match:
                district_id = district_id_match.group(1)

                district_links.append({
                    "District": name,
                    "District ID": district_id,
                    "URL": full_url
                })

    #Remove duplicate district links
    unique = {}
    for item in district_links:
        unique[item["District"]] = item

    return list(unique.values())

def scrape_current_page(url, district_name):
    """
    Current page format:
    序号 / 日期 / 二手房 / 新房 / 套均价
    """
    html = get_html(url)
    rows = html.xpath("//table//tr")

    data = []

    for row in rows:
        cells = row.xpath("./th | ./td")
        values = [clean_text("".join(cell.xpath(".//text()"))) for cell in cells]
        values = [v for v in values if v != ""]

        if len(values) >= 4 and values[0].isdigit():
            date = values[1]

            if re.match(r"202[3-6]-\d{2}", date):
                data.append({
                    "District": district_name,
                    "Date": date,
                    "Second-hand price (yuan/m²)": re.sub(r"[^\d.]", "", values[2]),
                    "New house price (yuan/m²)": re.sub(r"[^\d.]", "", values[3]),
                    "Source URL": url
                })

    return data

def scrape_year_page(url, year, district_name):
    """
    Year page format:
    月份 / 二手房均价 / 新房均价
    """
    html = get_html(url)
    rows = html.xpath("//table//tr")

    data = []

    for row in rows:
        cells = row.xpath("./th | ./td")
        values = [clean_text("".join(cell.xpath(".//text()"))) for cell in cells]
        values = [v for v in values if v != ""]

        if len(values) >= 3 and "月" in values[0]:
            month = values[0].replace("月", "").zfill(2)
            date = f"{year}-{month}"

            data.append({
                "District": district_name,
                "Date": date,
                "Second-hand price (yuan/m²)": re.sub(r"[^\d.]", "", values[1]),
                "New house price (yuan/m²)": re.sub(r"[^\d.]", "", values[2]),
                "Source URL": url
            })

    return data

def scrape_one_district(district_name, district_id, district_url):
    urls = [
        district_url,
        f"https://fangjia.gotohui.com/years/{district_id}/2025/",
        f"https://fangjia.gotohui.com/years/{district_id}/2024/",
        f"https://fangjia.gotohui.com/years/{district_id}/2023/"
    ]

    all_data = []

    for url in urls:
        print(f"Scraping {district_name}: {url}")

        try:
            if f"fjdata-{district_id}" in url:
                page_data = scrape_current_page(url, district_name)
            else:
                year = int(url.rstrip("/").split("/")[-1])
                page_data = scrape_year_page(url, year, district_name)

            print("Rows scraped:", len(page_data))
            all_data.extend(page_data)

            time.sleep(1)

        except Exception as e:
            print("Failed:", url)
            print("Reason:", e)

    unique_data = {}

    for row in all_data:
        unique_data[row["Date"]] = row

    final_data = list(unique_data.values())

    final_data = [
        row for row in final_data
        if "2023-" <= row["Date"] <= "2026-12"
    ]

    # Sort by date in descending order
    final_data = sorted(final_data, key=lambda x: x["Date"], reverse=True)

    return final_data

# 1. Automatically get all district links
district_links = get_district_links(start_url)

print("Districts found:")
for item in district_links:
    print(item["District"], item["District ID"], item["URL"])

all_district_data = []

# 2. Scrape each district separately and generate individual CSV files
for item in district_links:
    district_name = item["District"]
    district_id = item["District ID"]
    district_url = item["URL"]

    district_data = scrape_one_district(district_name, district_id, district_url)
    all_district_data.extend(district_data)

    safe_name = district_name_en.get(district_name, f"district_{district_id}")

    output_file = data_folder / f"{safe_name}_history_price_2023_2026.csv"


    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Date",
                "Second-hand price (yuan/m²)",
                "New house price (yuan/m²)",
                "Source URL"
            ]
        )

        writer.writeheader()

        for row in district_data:
            writer.writerow({
                "Date": row["Date"],
                "Second-hand price (yuan/m²)": row["Second-hand price (yuan/m²)"],
                "New house price (yuan/m²)": row["New house price (yuan/m²)"],
                "Source URL": row["Source URL"]
            })

    print("Saved:", output_file)
    print("-" * 60)

# 3. Generate a combined CSV file for all districts
combined_file = data_folder / "shanghai_all_districts_history_price_2023_2026.csv"


all_district_data = sorted(
    all_district_data,
    key=lambda x: (x["District"], x["Date"])
)

with open(combined_file, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "District",
            "Date",
            "Second-hand price (yuan/m²)",
            "New house price (yuan/m²)",
            "Source URL"
        ]
    )

    writer.writeheader()
    writer.writerows(all_district_data)

print("All finished!")
print("Total district files:", len(district_links))
print("Total rows:", len(all_district_data))
print("Combined file saved as:", combined_file)