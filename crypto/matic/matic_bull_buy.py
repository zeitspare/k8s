#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 10:17:46 2024

@author: sureshkumar.ramachandran
"""

# Buy Script

from binance.client import Client
import os
import configparser
import time

config = configparser.ConfigParser()
config.read('/Users/sureshkumar.ramachandran/AWS/aws_credentials/aws_configuration/zeitspare_trade_binance_config.ini')

binance_access_key_id = config.get('binance', 'binance_access_key_id')
binance_secret_access_key = config.get('binance', 'binance_secret_access_key')

assets_pairs = ["MATICUSDT"]
buy_price = 0.8750
spend_amount = 300
quantity_to_buy = round(spend_amount / buy_price)

client = Client(binance_access_key_id, binance_secret_access_key)

def execute_buy_market_order(pair, quantity):
    try:
        order = client.create_test_order(
            symbol=pair,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        print(f"MATIC Buy Order Executed: Buy Order Details \n {order}")
    except Exception as e:
        print(f"Error executing MATIC Buy Order: Error Details \n {e}")

def initial_waiting_loop():
    while True:
        try:
            # Check if the current price is greater than the buy price
            ticker = client.get_ticker(symbol=assets_pairs[0])
            current_price = float(ticker['lastPrice'])
            
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")

            print(f"MATIC Current Price ({current_price} USDT) - Waiting Price Rise ({buy_price} USDT)")

            if current_price > buy_price:
                print(f"MATIC Current Price ({current_price} USDT) greater than ({buy_price} USDT) at {current_time}. \n Starting To Buy MATIC")
                execute_buy_market_order(assets_pairs[0], quantity_to_buy)
                break  # Exit the initial waiting loop once the buy order is executed

            time.sleep(3)  # Sleep for 3 seconds before the next iteration

        except Exception as e:
            print(f"Error in initial waiting loop: {e}")
            time.sleep(3)  # Sleep for 3 seconds and retry

if __name__ == "__main__":
    initial_waiting_loop()
