import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from fuzzywuzzy import fuzz
import logging
import time

# Set up logging
logging.basicConfig(filename='scraping_log.txt', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def clean_name(name):
    """Standardize politician names"""
    return re.sub(r'[^\w\s]', '', name).lower().strip()

def fuzzy_match(name, name_list, threshold=80):
    """Fuzzy match names"""
    matches = [n for n in name_list if fuzz.ratio(clean_name(name), clean_name(n)) > threshold]
    return matches[0] if matches else name

def parse_amount(amount_str):
    """Parse amount strings, handling ranges"""
    if '-' in amount_str:
        low, high = map(lambda x: float(x.replace('$', '').replace(',', '')), amount_str.split('-'))
        return (low + high) / 2
    return float(amount_str.replace('$', '').replace(',', ''))

def scrape_trades():
    driver = webdriver.Chrome()
    url = 'https://www.capitoltrades.com/trades'
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table')

    data = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        try:
            date = cols[0].text.strip()
            politician = cols[1].text.strip()
            stock_name = cols[2].find('div', class_='name').text.strip()
            stock_ticker = cols[2].find('div', class_='ticker').text.strip()
            transaction = cols[3].text.strip()
            amount = cols[4].text.strip()

            data.append([date, politician, stock_name, stock_ticker, transaction, amount])
        except Exception as e:
            logging.error(f"Error parsing row: {e}")

    driver.quit()
    return data

def process_data(data):
    columns = ['Date', 'Politician', 'Stock Name', 'Stock Ticker', 'Transaction', 'Amount']
    df = pd.DataFrame(data, columns=columns)

    # Clean and standardize data
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Politician'] = df['Politician'].apply(clean_name)
    df['Amount'] = df['Amount'].apply(parse_amount)

    # Handle missing data
    df['Stock Ticker'] = df['Stock Ticker'].fillna('UNKNOWN')
    df = df.dropna(subset=['Date', 'Politician', 'Stock Name', 'Transaction'])

    # Fuzzy match politician names
    unique_politicians = df['Politician'].unique()
    df['Politician'] = df['Politician'].apply(lambda x: fuzzy_match(x, unique_politicians))

    return df

def main():
    try:
        raw_data = scrape_trades()
        df = process_data(raw_data)
        
        # Save to CSV
        df.to_csv('congressional_trades.csv', index=False)
        logging.info(f"Scraped and processed {len(df)} trades")
        print(df.head())
        
        # Data integrity checks
        logging.info(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        logging.info(f"Number of unique politicians: {df['Politician'].nunique()}")
        logging.info(f"Number of unique stocks: {df['Stock Ticker'].nunique()}")
        logging.info(f"Amount range: ${df['Amount'].min()} to ${df['Amount'].max()}")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()