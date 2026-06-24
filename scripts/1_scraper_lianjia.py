#!/usr/bin/env python
# coding: utf-8

# # Lianjia Scraper
# **Link:** sh.lianjia.com (second-hand listings + rental listings)  
# **Coverage:** All 16 Shanghai districts
# 
# ---
# 

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# In[ ]:


PAGES_PER_DISTRICT = 5
MIN_WAIT = 8
MAX_WAIT = 12
DISTRICTS = [   
    "huangpu",    
    "jingan",     
    "xuhui",      
    "changning", 
    "putuo",     
    "hongkou",    
    "yangpu",     
    "pudong",     
    "baoshan",    
    "minhang",   
    "jiading",   
    "songjiang", 
    "qingpu",    
    "fengxian",   
    "jinshan",    
    "chongming",  
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
    "Cookie": #take active cookie info from active session if needed "lianjia_ssid=9ef6d032-a079-4c6e-aa8e-fd0beb52398c; lianjia_uuid=7c463e68-cd48-4716-b422-8c253bc7c7f4; crosSdkDT2019DeviceId=41jum4-j3e6x6-jm0rhs2x9qdb8m0-qji8x3kq9; hip=TyhAqtPiaXlN58mAWvlpGcQIkF619WZJbPm5YT4D3Y60JR3ThISLx4HxzRsyHzS0YnelYBoduDbOdXYCd71Ac_GMj91AzVRycL2dfOnsVl7HxHraCQbtwbbeC4DYQF119qaT96z01zGMpZDfC7MophH5ORx4F03uCc_WbAu1nn-D7Yg9ps4OlGwVLK2MlJIGHU1Cd3D49yV5r_XxJytS5BXV7lpeiO2eLvUdlksIWB_IVw0wzA31LHIlYg%3D%3D; select_city=310000; Hm_lvt_46bf127ac9b856df503ec2dbf942b67e=1780486787; HMACCOUNT=AA1CD3FE5053A297; _jzqa=1.1932488731849971500.1780486788.1780486788.1780486788.1; _jzqc=1; _jzqckmp=1; _qzjc=1; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2219e8d48532919-0521753d79623b8-26061151-1474560-19e8d48532a17a1%22%2C%22%24device_id%22%3A%2219e8d48532919-0521753d79623b8-26061151-1474560-19e8d48532a17a1%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _ga=GA1.2.1235293128.1780486799; _gid=GA1.2.1463941632.1780486799; login_ucid=2000000541677282; lianjia_token=2.00156586294fa5bd2704c8af1806e8514c; lianjia_token_secure=2.00156586294fa5bd2704c8af1806e8514c; security_ticket=sC+ixt0/3+5u2vHV+oYTiN7vu0SxzjL+lan3QOwKFFW+mRUwF5/9TzgI86C4Tqm5LtAFgCkVPRAJ/n5P+O/MUpRDWYnA4zZhgfTKe19JOCTWIx2fkfUxx+7FH7ivb4ybesht9pFWH9XjO28YxdwtiHEaqM44RQYzY83E9HOqh+k=; ftkrc_=8c36b81c-66bc-4e85-a9e1-f40c6f72345d; lfrc_=da0c1bc9-cbdb-49b8-bb70-53b246bfb564; Hm_lpvt_46bf127ac9b856df503ec2dbf942b67e=1780487074; _qzja=1.74506134.1780486787874.1780486787874.1780486787874.1780486787874.1780487074378.0.0.0.2.1; _qzjb=1.1780486787874.2.0.0.0; _qzjto=2.1.0; _jzqb=1.2.10.1780486788.1; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1; _ga_LRLL77SF11=GS2.2.s1780486799$o1$g1$t1780487085$j60$l0$h0; _ga_GVYN2J1PCG=GS2.2.s1780486799$o1$g1$t1780487085$j60$l0$h0; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZGEwZmM3ZTUxMDA5OGQ1YzE3Mjk3NmRhMTVhMjBjODY2N2FkMGEyNWVmN2I3M2I2OGUxNTVjNGYyOWYyNzljZDdmY2NmZjNjMDYzNDAwNjE0MmM0NGIzOTZjNDJkMTNmMTMxYzU4MmFhYmI5NTY5ZjM3NjVkOTNlMGJlNTE1NWE2MDBhNDMyODI5YjM5MzQwOWM0ZWQ4MWEyMDdmM2Q5ZDMxNjcyNzcyOWU3ODFhZTIyZTkxZGIxM2Y3YzVhNDMxMzc1NjQ1NTZiZDgzNWFlZmUwNGNkMDliNTYwOWE0MDk3MmJhMjU1YzQ1ZDlmMzA3ZjgyZTIwNDFkYjg5MzJiMVwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI4YzVlZTU5ZlwifSIsInIiOiJodHRwczovL3NoLmxpYW5qaWEuY29tL2Vyc2hvdWZhbmcvcHV0dW8vIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=",
    "Referer": "https://sh.lianjia.com/ershoufang/",
}


# In[ ]:


# open chrome through terminal "chrome.exe --remote-debugging-port=9222"
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)
print("Connected:", driver.title)


# 
# ## Buy Listings (二手房)
# 
# URL pattern: `https://sh.lianjia.com/ershoufang/{district}/pg{page}/`  
# 
# Fields we're grabbing per listing:
# - Title (e.g. "3-bedroom in Lujiazui")
# - District
# - Community name (小区)
# - House info (layout, size, floor, direction, age)
# - Total price (万元)
# - Unit price (元/sqm)
# - Tags 
# - Listing URL

# In[ ]:


def get_page(url):
     return get_page_reuse(url)

def get_page_reuse(url):
    driver.get(url) 
    time.sleep(random.uniform(3, 5))

    page_src = driver.page_source

    captcha_triggers = ["验证", "滑动", "拖动", "人机", "captcha"]
    if any(word in page_src[:3000] for word in captcha_triggers):
        print(f"\n  CAPTCHA")
        input("  Press Enter when done: ")
        time.sleep(2)

    return BeautifulSoup(driver.page_source, "html.parser")

def parse_buy_listing(item, district):
    """
    Pull data from a single listing card on the ershoufang page.
    Returns a dict, or None if something important is missing.
    """
    try:
        title_tag = item.select_one(".title a")
        title = title_tag.get_text(strip=True) if title_tag else ""
        listing_url = title_tag["href"] if title_tag else ""
        community_tag = item.select_one(".positionInfo a")
        community = community_tag.get_text(strip=True) if community_tag else ""

        info_tag = item.select_one(".houseInfo")
        house_info = info_tag.get_text(strip=True) if info_tag else ""

        total_price_tag = item.select_one(".totalPrice .value")
        if not total_price_tag:
            total_price_tag = item.select_one(".totalPrice")
        total_price_text = total_price_tag.get_text(strip=True) if total_price_tag else ""

        unit_price_tag = item.select_one(".unitPrice .value")
        if not unit_price_tag:
            unit_price_tag = item.select_one(".unitPrice span")
        unit_price_text = unit_price_tag.get_text(strip=True) if unit_price_tag else ""

        tags = [t.get_text(strip=True) for t in item.select(".tag span")]

        return {
            "district": district,
            "community": community,
            "title": title,
            "house_info": house_info,
            "total_price_wan": total_price_text,  
            "unit_price_raw": unit_price_text,    
            "tags": "|".join(tags),
            "listing_url": listing_url,
        }

    except Exception as e:
        return None


def scrape_buy_district(district, pages=PAGES_PER_DISTRICT):
    """Scrape all buy listings for one district across multiple pages."""
    results = []
    base_url = f"https://sh.lianjia.com/ershoufang/{district}/pg{{page}}/"

    for page in range(1, pages + 1):
        url = base_url.format(page=page)
        soup = get_page_reuse(url)

        if soup is None:
            print(f"  Skipping page {page} (failed to load)")
            continue

        listings = soup.select(".sellListContent li.clear")

        if not listings:
            listings = soup.select(".listContent li")
        if not listings:
            listings = soup.select("li.clear")

        if not listings:
            print(f" No listings found on page {page}")
            break  

        for item in listings:
            data = parse_buy_listing(item, district)
            if data and data["total_price_wan"]:
                results.append(data)

        print(f"  Page {page}: got {len(listings)} listings")
        if page % 5 == 0 and page < pages:
            long_wait = random.uniform(15, 25)
            print(f" Break")
            time.sleep(long_wait)
        elif page < pages:
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))

    return results


# In[ ]:


all_buy_listings = []

for district in DISTRICTS:
    print(f"\n[{DISTRICTS.index(district)+1}/{len(DISTRICTS)}] Scraping buy listings: {district}")
    listings = scrape_buy_district(district)
    all_buy_listings.extend(listings)
    print(f"  → Total so far: {len(all_buy_listings)} listings")

    if district != DISTRICTS[-1]:
        wait = random.uniform(3, 6)
        print(f"  Waiting {wait:.1f}s before next district...")
        time.sleep(wait)

print(f"\n Completed - Total BUY listings scraped: {len(all_buy_listings)}")


# 
# ## Rental Listings (租房)
# 
# URL pattern: `https://sh.lianjia.com/zufang/{district}/pg{page}/`

# In[ ]:


#trial fixed 

def parse_rent_listing(item, district):
    try:
        title_tag = item.select_one(".content__list--item--title a")
        title = title_tag.get_text(strip=True) if title_tag else ""
        listing_url = "https://sh.lianjia.com" + title_tag["href"] if title_tag and title_tag.get("href") else ""

        des_tag = item.select_one(".content__list--item--des")
        des_text = des_tag.get_text(separator=" ", strip=True) if des_tag else ""

        location_links = des_tag.select("a") if des_tag else []
        location_parts = [a.get_text(strip=True) for a in location_links]
        community = location_parts[-1] if location_parts else ""

        area_match = re.search(r"([\d.]+)\s*(?:㎡|m²|平)", des_text)
        area_sqm = float(area_match.group(1)) if area_match else None

        orientation_match = re.search(r"[东西南北]{1,2}(?=\s|$)", des_text)
        orientation = orientation_match.group(0) if orientation_match else ""
        layout_match = re.search(r"\d+室\d*厅?\d*卫?", des_text)
        layout = layout_match.group(0) if layout_match else ""

        tags = [t.get_text(strip=True) for t in item.select("i[class*='content__item__tag']")]

        price_tag = item.select_one(".content__list--item-price em")
        rent_yuan = int(price_tag.get_text(strip=True)) if price_tag else None

        rent_per_sqm = round(rent_yuan / area_sqm, 1) if rent_yuan and area_sqm else None

        return {
            "district": district,
            "community": community,
            "title": title,
            "area_sqm": area_sqm,
            "layout": layout,
            "orientation": orientation,
            "monthly_rent_yuan": rent_yuan,
            "rent_per_sqm": rent_per_sqm,
            "tags": "|".join(tags),
            "listing_url": listing_url,
        }

    except Exception as e:
        return None

def scrape_rent_district(district, pages=PAGES_PER_DISTRICT):
    results = []
    base_url = f"https://sh.lianjia.com/zufang/{district}/pg{{page}}/"

    for page in range(1, pages + 1):
        url = base_url.format(page=page)
        print(f"  Page {page}...", end=" ", flush=True)

        driver.get(url)
        time.sleep(3)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        if any(w in driver.page_source[:3000] for w in ["验证", "滑动", "拖动", "人机"]):
            print(f"\n  CAPTCHA!")
            input("  Press Enter when done: ")
            time.sleep(3)

        items = driver.execute_script("""
            let results = [];
            let items = document.querySelectorAll('.content__list--item');

            items.forEach(function(item) {

                let priceEl = item.querySelector('.content__list--item-price em');
                let price = priceEl ? priceEl.innerText.trim() : '';


                let titleEl = item.querySelector('.content__list--item--title a');
                let title = titleEl ? titleEl.innerText.trim() : '';
                let url = titleEl ? titleEl.getAttribute('href') : '';


                let desEl = item.querySelector('.content__list--item--des');
                let des = desEl ? desEl.innerText.trim() : '';
                let tagEls = item.querySelectorAll('i[class*="content__item__tag"]');
                let tags = Array.from(tagEls).map(t => t.innerText.trim()).join('|');

                results.push({
                    title: title,
                    url: url,
                    des: des,
                    price: price,
                    tags: tags
                });
            });

            return results;
        """)

        if not items:
            print("check if page loaded")
            break
        page_results = []
        for item in items:
            try:
                des_text = item["des"]

                area_match = re.search(r"([\d.]+)\s*(?:㎡|m²|平)", des_text)
                area_sqm = float(area_match.group(1)) if area_match else None


                layout_match = re.search(r"\d+室\d*厅?\d*卫?", des_text)
                layout = layout_match.group(0) if layout_match else ""

                orient_match = re.search(r"[东西南北]{1,2}(?=\s|/|$)", des_text)
                orientation = orient_match.group(0) if orient_match else ""

                parts = [p.strip() for p in des_text.replace("\n", " ").split("-") if p.strip()]
                community = parts[-1].split("/")[0].strip() if parts else ""

                rent_yuan = int(item["price"]) if item["price"].isdigit() else None
                rent_per_sqm = round(rent_yuan / area_sqm, 1) if rent_yuan and area_sqm else None

                listing_url = "https://sh.lianjia.com" + item["url"] if item["url"] else ""

                page_results.append({
                    "district": district,
                    "community": community,
                    "title": item["title"],
                    "area_sqm": area_sqm,
                    "layout": layout,
                    "orientation": orientation,
                    "monthly_rent_yuan": rent_yuan,
                    "rent_per_sqm": rent_per_sqm,
                    "tags": item["tags"],
                    "listing_url": listing_url,
                })
            except Exception as e:
                continue

        results.extend(page_results)
        print(f"got {len(page_results)} listings")

        if page % 5 == 0 and page < pages:
            wait = random.uniform(15, 25)
            print(f" Break")
            time.sleep(wait)
        elif page < pages:
            time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))

    return results


# In[ ]:


all_rent_listings = []

for district in DISTRICTS:
    print(f"\n[{DISTRICTS.index(district)+1}/{len(DISTRICTS)}] Scraping rent listings: {district}")
    listings = scrape_rent_district(district)
    all_rent_listings.extend(listings)
    print(f"  → Total so far: {len(all_rent_listings)} listings")

    if district != DISTRICTS[-1]:
        wait = random.uniform(3, 6)
        time.sleep(wait)

print(f"\nCompleted - Total rental listings scraped: {len(all_rent_listings)}")


# ## Save RAW Data

# In[ ]:


from pathlib import Path
today = datetime.now().strftime("%Y%m%d")

df_buy_raw = pd.DataFrame(all_buy_listings)
df_rent_raw = pd.DataFrame(all_rent_listings)

project_root = Path.cwd().parent
data_dir = project_root / "data" / "raw"

df_buy_raw.to_csv(data_dir / f"lianjia_buy_raw_{today}.csv", index=False, encoding="utf-8-sig")
df_rent_raw.to_csv(data_dir / f"lianjia_rent_raw_{today}.csv", index=False, encoding="utf-8-sig")

print(f"Raw buy data: {df_buy_raw.shape[0]} rows × {df_buy_raw.shape[1]} cols")
print(f"Raw rent data: {df_rent_raw.shape[0]} rows × {df_rent_raw.shape[1]} cols")
print(f"\nSaved as:")
print(f"  lianjia_buy_raw_{today}.csv")
print(f"  lianjia_rent_raw_{today}.csv")


# ## Data Cleaning

# In[ ]:


df_buy = df_buy_raw.copy()

def parse_house_info(info_str):
    """Break the house info string into individual fields."""
    parts = [p.strip() for p in str(info_str).split("|")]

    layout = ""
    area_sqm = None
    floor_level = ""
    orientation = ""
    build_year = None

    for part in parts:
        if "室" in part or "房" in part:
            layout = part
        elif "平米" in part or "㎡" in part:
            nums = re.findall(r"[\d.]+", part)
            if nums:
                area_sqm = float(nums[0])
        elif "楼层" in part or "层" in part:
            floor_level = part
        elif "朝" in part or "南" in part or "北" in part or "东" in part or "西" in part:
            orientation = part
        elif "年" in part and "建" in part:
            nums = re.findall(r"\d{4}", part)
            if nums:
                build_year = int(nums[0])

    return layout, area_sqm, floor_level, orientation, build_year


parsed = df_buy["house_info"].apply(parse_house_info)
df_buy[["layout", "area_sqm", "floor_level", "orientation", "build_year"]] = pd.DataFrame(
    parsed.tolist(), index=df_buy.index
)

def clean_total_price(price_str):
    nums = re.findall(r"[\d.]+", str(price_str))
    return float(nums[0]) if nums else None

df_buy["total_price_wan"] = df_buy["total_price_wan"].apply(clean_total_price)
df_buy["total_price_yuan"] = df_buy["total_price_wan"] * 10000  # convert 万 to 元
0
def clean_unit_price(price_str):
    cleaned = str(price_str).replace(",", "")
    nums = re.findall(r"\d+", cleaned)
    return int(nums[0]) if nums else None

df_buy["unit_price_yuan_sqm"] = df_buy["unit_price_raw"].apply(clean_unit_price)


mask = df_buy["unit_price_yuan_sqm"].isna() & df_buy["total_price_yuan"].notna() & df_buy["area_sqm"].notna()
df_buy.loc[mask, "unit_price_yuan_sqm"] = (
    df_buy.loc[mask, "total_price_yuan"] / df_buy.loc[mask, "area_sqm"]
).round(0)

df_buy["scraped_date"] = today
df_buy["listing_type"] = "buy"

df_buy = df_buy.drop(columns=["unit_price_raw"])

print(f"After cleaning: {df_buy.shape[0]} rows")
print("\nOverview:")
print(df_buy.dtypes)


# In[ ]:


before = len(df_buy)

df_buy = df_buy.drop_duplicates(subset=["listing_url"])
df_buy = df_buy.dropna(subset=["unit_price_yuan_sqm"])

df_buy = df_buy[
    (df_buy["unit_price_yuan_sqm"] >= 5000) &
    (df_buy["unit_price_yuan_sqm"] <= 1_000_000)
]

df_buy = df_buy[
    df_buy["area_sqm"].isna() |  
    ((df_buy["area_sqm"] >= 10) & (df_buy["area_sqm"] <= 1000))
]

after = len(df_buy)
print(f"Rows removed during cleaning: {before - after}")
print(f"Final buy dataset: {after} listings")

df_buy.head(3)


# In[ ]:


print("BUY DATA SUMMARY")
print(f"\nListings per district:")
print(df_buy["district"].value_counts().to_string())

print(f"\nUnit price (元/sqm) by district:")
print(df_buy.groupby("district")["unit_price_yuan_sqm"].agg(["mean", "median", "count"]).round(0).to_string())

print(f"\nMissing values:")
print(df_buy.isnull().sum()[df_buy.isnull().sum() > 0].to_string())


# In[ ]:


from pathlib import Path

project_root = Path.cwd().parent
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

buy_cols = [
    "scraped_date", "listing_type",
    "district", "community", "title",
    "layout", "area_sqm", "floor_level", "orientation", "build_year",
    "total_price_wan", "total_price_yuan", "unit_price_yuan_sqm",
    "tags", "listing_url", "house_info"
]

rent_cols = [
    "scraped_date", "listing_type",
    "district", "title",
    "layout", "area_sqm",
    "monthly_rent_yuan", "rent_per_sqm",
    "location_tags", "listing_url", "house_info"
]

buy_cols_exist = [c for c in buy_cols if c in df_buy.columns]
rent_cols_exist = [c for c in rent_cols if c in df_rent.columns]

df_buy_final = df_buy[buy_cols_exist]
df_rent_final = df_rent[rent_cols_exist]

buy_filename = data_dir / f"lianjia_buy_clean_{today}.csv"
rent_filename = data_dir / f"lianjia_rent_clean_{today}.csv"

df_buy_final.to_csv(buy_filename, index=False, encoding="utf-8-sig")
df_rent_final.to_csv(rent_filename, index=False, encoding="utf-8-sig")
print("Completed")

