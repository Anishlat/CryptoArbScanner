import json
from time import sleep
from pycoingecko import CoinGeckoAPI
import pandas as pd
import requests
import asyncio
import aiohttp
import sys
import asyncio

# Initialize CoinGecko API
cg = CoinGeckoAPI()

# Global variable to store the coin data
coin_data_global = {}

# Handle the asynchronous fetching of coin data and store the results in a global variable.
async def fetch_data_periodically():
    while True:
        # Fetch the coin data
        coin_data = await get_coin_data(15)
        # Print a summary of the fetched data
        print(f"Fetched data for {len(coin_data)} coins")
        # Store the result in the global variable
        global coin_data_global
        coin_data_global = coin_data
        # Wait for a specified interval before fetching again
        await asyncio.sleep(220) # Adjust the interval as needed


# Function to calculate percent difference between two numbers
def get_change(a, b):
    if a == b:
        return 0
    try:
        return (abs(a - b) / b) * 100.0
    except ZeroDivisionError:
        return float('inf')

# ------------------------------------------------------------------------------------------------------------
'''
# DEX Scanning Code (Currently only showing 0 values)

# Function to calculate profit from given ticker data (cg.get_coin_ticker_by_id)
def get_profit(coin_data):
    tickers = coin_data['tickers']
    prices = {}

    # List of decentralized exchanges
    dexs = ['Uniswap', 'Sushiswap', 'Balancer', 'Curve', '1inch', 'Kyber Network', '0xProtocol']

    # Sort through all exchanges (with high trust scores) and add to dictionary
    for exchange in tickers:
        if (
            (exchange['target'] == 'USDT' or exchange['target'] == 'USD') and
             exchange['trust_score'] == 'green' and
             exchange['market']['name'] in dexs  # Only include decentralized exchanges
        ):
            prices[str(exchange['market']['name'])] = exchange['last']

    # Calculate highest and lowest from dictionary
    high = max(prices, key=prices.get, default=0)
    low = min(prices, key=prices.get, default=0)

    # Calculate profit from potential trade
    if (high == 0 or low == 0):
        profit = 0
    else:
        profit = get_change(prices[low], prices[high])

    return profit, high, low
'''
# ------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------
# CEX Scanning Code 
def get_profit(coin_data):
    tickers = coin_data['tickers']

    prices = {}

    # sort through all exchanges (with high trust scores) and add to dictionary 
    for exchange in tickers:
        if (
            (exchange['target'] == 'USDT' or exchange['target'] == 'USD') and
             exchange['trust_score'] == 'green' and
             exchange['market']['name'] != 'eToroX' # does not allow withdraw of crypto
        ):
            prices[str(exchange['market']['name'])] = exchange['last']
    
    # calculate hgihest and lowest from dictionary
    high = max(prices, key=prices.get, default=0)
    low = min(prices, key=prices.get, default=0)
    
    # calculate profit from potential trade
    if (high == 0 or low == 0):
        profit = 0
    else:
        profit = get_change(prices[low], prices[high])

    return profit, high, low
# ------------------------------------------------------------------------------------------------------------

# Function to return an array of top coins from CoinGecko
# Asynchronous function to fetch coin data
async def fetch_coin_data(session, coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/tickers"
    async with session.get(url) as response:
        return await response.json()

# Asynchronous function to get coin data for multiple coins
async def get_coin_data(numCoins):
    coin_tickers = {}
    coin_list = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc')
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_coin_data(session, coin['id']) for coin in coin_list[:numCoins]]
        results = await asyncio.gather(*tasks)
        for coin, result in zip(coin_list[:numCoins], results):
            coin_tickers[coin['id']] = result
    return coin_tickers


# Function to get possible trades based on coin data
def get_trades(coin_data):
    possible_trades = {}

    # Get most profitable trade for each coin
    for ticker in coin_data:
        profit, highExchange, lowExchange = get_profit(coin_data[ticker])

        possible_trades[ticker] = {
            'symbol': ticker,
            'profit': profit,
            'highExchange': highExchange,
            'lowExchange': lowExchange
        }

    # Tether provides lots of false negatives, so remove it
    del possible_trades['tether']

    return possible_trades

# Function to find the highest profit trade from possible trades
def suggest_trade(possible_trades):
    max_profit_ticker = ''
    max_profit = 0
    max_profit_highExchange = ''
    max_profit_lowExchange = ''

    # Find the most profitable trade
    for trade in possible_trades:
        if possible_trades[trade]['profit'] > max_profit:
            highExchange = possible_trades[trade]['highExchange']
            lowExchange = possible_trades[trade]['lowExchange']

            max_profit = possible_trades[trade]['profit']
            max_profit_ticker = trade
            max_profit_highExchange = highExchange
            max_profit_lowExchange = lowExchange

    print("highest profit trade is with: " + max_profit_ticker + " for a profit of " + str(max_profit))
    print("buy " + max_profit_ticker + " on " + max_profit_lowExchange + " and sell on " + max_profit_highExchange)

# Function to create and sort a DataFrame with a key from a dictionary
def create_sorted_dataframe(data, sort_key):
    df = pd.DataFrame(data).T
    df.fillna(0, inplace=True)
    df.sort_values(by=sort_key, ascending=False, inplace=True)

    return df

# Test code (uncomment to run)
'''
async def main():
    coin_data = await get_coin_data(5)
    possible_trades = get_trades(coin_data)
    suggest_trade(possible_trades)
    sorted_trades_df = create_sorted_dataframe(possible_trades, 'profit')
    print(sorted_trades_df)

asyncio.run(main())
'''