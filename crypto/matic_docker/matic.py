#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 23:10:23 2023

@author: sureshkumar.ramachandran
"""

import logging
from binance.client import Client
import os
import time

# Specify Binance credentials
binance_access_key_id = os.environ.get('BINANCE_ACCESS_KEY')
binance_secret_access_key = os.environ.get('BINANCE_SECRET_KEY')

# Specify assets, asset pairs, buy and sell prices
assets_pairs = ["MATICUSDT"]

buy_price = float(os.environ.get('BUY_PRICE'))
sell_price = float(os.environ.get('SELL_PRICE'))
spend_amount = float(os.environ.get('SPEND_AMOUNT'))

# Specify trading parameters
quantity_to_buy = round(spend_amount / buy_price)  # Quantity to buy in MATIC
quantity_to_sell = quantity_to_buy  # Quantity to sell in MATIC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

client = Client(binance_access_key_id, binance_secret_access_key)

def execute_buy_order(pair, quantity):
    try:
        order = client.create_test_order(
            symbol=pair,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        logger.info(f"Buy Order Executed: {order}")
    except Exception as e:
        logger.error(f"Error executing buy order: {e}")

def execute_sell_order(pair, quantity):
    try:
        order = client.create_test_order(
            symbol=pair,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        logger.info(f"Sell Order Executed: {order}")
    except Exception as e:
        logger.error(f"Error executing sell order: {e}")

def check_buy_condition(pair, buy_price, quantity_to_buy):
    try:
        # Get ticker information for the specified pair
        ticker = client.get_ticker(symbol=pair)
        current_price = float(ticker['lastPrice'])

        logger.info(f"Current Price for {pair}: {current_price} USDT - Waiting to Buy")

        # Check buy condition
        if current_price <= buy_price:
            execute_buy_order(pair, quantity_to_buy)
            return True  # Return True if buy order is executed

    except Exception as e:
        logger.error(f"Error checking buy condition: {e}")

    return False

def check_sell_condition(pair, sell_price, quantity_to_sell):
    try:
        # Get ticker information for the specified pair
        ticker = client.get_ticker(symbol=pair)
        current_price = float(ticker['lastPrice'])

        logger.info(f"Current Price for {pair}: {current_price} USDT - Waiting to Sell")

        # Check sell condition
        if current_price >= sell_price:
            execute_sell_order(pair, quantity_to_sell)
            return True  # Return True if sell order is executed

    except Exception as e:
        logger.error(f"Error checking sell condition: {e}")

    return False

def trading_loop():
    state = "buy"  # Initial state is "buy"

    while True:
        try:
            if state == "buy":
                buy_executed = check_buy_condition(assets_pairs[0], buy_price, quantity_to_buy)
                if buy_executed:
                    state = "sell"  # Change state to "sell" after buy order is executed

            elif state == "sell":
                sell_executed = check_sell_condition(assets_pairs[0], sell_price, quantity_to_sell)
                if sell_executed:
                    break  # Exit the loop after sell order is executed

            time.sleep(2)  # Sleep for 2 seconds before the next iteration

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            time.sleep(2)  # Sleep for 2 seconds and retry

if __name__ == "__main__":
    trading_loop()

