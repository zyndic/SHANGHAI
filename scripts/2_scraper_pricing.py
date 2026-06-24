#!/usr/bin/env python
# coding: utf-8

# # Historical Housing Prices Scraper
# **Link:**  `https://fangjia.gotohui.com/years/` (district-level)          
# **Coverage:** Annual average new housing price by district
# 
# ---

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://fangjia.gotohui.com/years/',
}

DISTRICTS = {
    'Huangpu':   2497,
    'Xuhui':     2487,
    'Changning': 2500,
    'Jingan':    2496,
    'Putuo':     2490,
    'Hongkou':   2498,
    'Yangpu':    2486,
    'Minhang':   2492,
    'Baoshan':   2501,
    'Jiading':   2495,
    'Pudong':    2491,
    'Jinshan':   2494,
    'Songjiang': 2488,
    'Qingpu':    2489,
    'Fengxian':  2499,
    'Chongming': 2502,
}

YEARS = list(range(2015, 2026))

print(f'Configured {len(DISTRICTS)} districts, years {YEARS[0]}–{YEARS[-1]}')


# In[ ]:


def scrape_one_price_page(district_name, district_id, year):
    url = f'https://fangjia.gotohui.com/years/{district_id}/{year}/'
    records = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) < 2:
                    continue
                month_text = cells[0].get_text(strip=True)
                price_text = cells[1].get_text(strip=True)

                month_match = re.search(r'(\d+)月', month_text)
                price_match = re.search(r'([\d,]+)', price_text)

                if month_match and price_match:
                    month = int(month_match.group(1))
                    price = float(price_match.group(1).replace(',', ''))
                    if 1 <= month <= 12 and price > 1000:
                        records.append({
                            'district':      district_name,
                            'district_id':   district_id,
                            'year':          year,
                            'month':         month,
                            'date':          f'{year}-{month:02d}',
                            'price_per_sqm': price,
                        })
    except requests.exceptions.RequestException as e:
        print(f'    ERROR: {district_name} {year} — {e}')
    return records


# In[ ]:


all_price_records = []

for district_name, district_id in DISTRICTS.items():
    district_rows = []
    for year in YEARS:
        rows = scrape_one_price_page(district_name, district_id, year)
        district_rows.extend(rows)
        time.sleep(0.4)

    all_price_records.extend(district_rows)
    years_found = sorted(set(r['year'] for r in district_rows))
    print(f'{district_name:12s} (ID {district_id}):  {len(district_rows):3d} monthly records  |  years: {years_found}')

print(f'\nTotal monthly price records scraped: {len(all_price_records)}')


# In[ ]:


from pathlib import Path

project_root = Path.cwd().parent
data_dir = project_root / "data"

data_dir.mkdir(exist_ok=True)

df_price = pd.DataFrame(all_price_records)
df_price['year']          = df_price['year'].astype(int)
df_price['month']         = df_price['month'].astype(int)
df_price['price_per_sqm'] = pd.to_numeric(df_price['price_per_sqm'], errors='coerce')
df_price = df_price.sort_values(['district', 'year', 'month']).reset_index(drop=True)

output_file = data_dir / "shanghai_housing_prices.csv"

df_price.to_csv(
    output_file,
    index=False,
    encoding='utf-8-sig'
)
print('Saved: shanghai_housing_prices.csv')
print(f'Shape: {df_price.shape}  |  Columns: {list(df_price.columns)}')
print()
df_price.head(14)


# In[ ]:


df_price_annual = (
    df_price
    .groupby(['district', 'district_id', 'year'])['price_per_sqm']
    .mean()
    .round(0)
    .reset_index()
    .rename(columns={'price_per_sqm': 'avg_annual_price_per_sqm'})
)

output_file = data_dir / "shanghai_housing_prices_annual.csv"

df_price_annual.to_csv(
    output_file,
    index=False,
    encoding='utf-8-sig'
)
print('Saved: shanghai_housing_prices_annual.csv')
print(f'Shape: {df_price_annual.shape}')
print()
print(df_price_annual.pivot(index='year', columns='district', values='avg_annual_price_per_sqm').to_string())

