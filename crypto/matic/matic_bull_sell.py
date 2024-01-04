#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 4 10:18:43 2024
@author: sureshkumar.ramachandran
"""

from binance.client import Client
import os
import configparser
import time

config = configparser.ConfigParser()
config.read('/Users/sureshkumar.ramachandran/AWS/aws_credentials/aws_configuration/zeitspare_trade_binance_config.ini')

binance_access_key_id = config.get('binance', 'binance_access_key_id')
binance_secret_access_key = config.get('binance', 'binance_secret_access_key')

assets_pairs = ["MATICUSDT"]
buy_price = 0.8689
sell_price = 0.8730
quantity_to_sell = 300  # Update with the actual quantity to sell

client = Client(binance_access_key_id, binance_secret_access_key)

def execute_sell_market_order(pair, quantity):
    try:
        order = client.create_test_order(
            symbol=pair,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        print(f"MATIC Sell MARKET Order Executed: Sell Order Details \n {order}")
    except Exception as e:
        print(f"Error executing MATIC Buy Order: Error Details \n {e}")

def execute_sell_limit_order(pair, quantity, price):
    try:
        order = client.create_test_order(
            symbol=pair,
            side='SELL',
            type='LIMIT',
            quantity=quantity,
            timeInForce='GTC',
            price=price
        )
        print(f"MATIC Sell LIMIT Order Executed at {price}: Sell Order Details \n {order}")
    except Exception as e:
        print(f"Error executing MATIC sell order: Error Details \n {e}")

def initial_waiting_loop_sell():
    dynamic_sell_price = sell_price  # Initialize dynamic_sell_price with the original sell_price

    while True:
        try:
            # Check if the current price is greater than the original sell price
            ticker = client.get_ticker(symbol=assets_pairs[0])
            current_price = float(ticker['lastPrice'])

            current_time = time.strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n MATIC Current Price ({current_price} USDT) - Waiting for Sell Price Rise ({dynamic_sell_price} USDT)")

            if current_price > dynamic_sell_price:
                dynamic_sell_price = current_price  # Increase the dynamic_sell_price
                print("\n MATIC NEW SELL PRICE INCREASED - SUCCESS")
                print(f"\n MATIC Current Price ({current_price} USDT)")
                print(f"\n MATIC New Sell Price ({dynamic_sell_price} USDT)")

            # Check if the current price is 0.7% less than the dynamic_sell_price
            percentage_difference = (1 - (current_price / dynamic_sell_price)) * 100
            print(f"\n Safe Percentage Difference to sell MATIC: {percentage_difference:.2f}% sells at 0.7%")
            
            # Check if the current price is 0.7% less than the dynamic_sell_price
            final_sell_price = round((dynamic_sell_price * 0.993), 4)
            Expected_profit_percentage = ((sell_price - buy_price)/buy_price) * 100

            if current_price <= final_sell_price:
                if final_sell_price > sell_price:
                    print(f"\n MATIC increased SEll Price:({final_sell_price} USDT) \n greater than expected sell price: ({sell_price} USDT) \n Starting To Sell MATIC at NEW SELL PRICE at {current_time}")
                    Achieved_profit_percentage = ((final_sell_price - sell_price)/sell_price) * 100
                    Total_profit_percentage = Expected_profit_percentage + Achieved_profit_percentage
                    print(f"\n Profit = Expected Profit: {Expected_profit_percentage:.2f}% + Increased Profit: {Achieved_profit_percentage:.2f}%")
                    print(f"\n Profit = {Total_profit_percentage:.2f}%")
                    execute_sell_limit_order(assets_pairs[0], quantity_to_sell, final_sell_price)
                else:
                    print(f"\n MATIC increased SEll Price:({final_sell_price} USDT) \n not performed at expected sell price: ({sell_price} USDT) \n Starting To Sell MATIC at DEFINED SELL PRICE at {current_time}")
                    print(f"Profit = {Expected_profit_percentage:.2f}%")
                    execute_sell_market_order(assets_pairs[0], quantity_to_sell)
                break  # Exit the initial waiting loop once the sell order is executed

            time.sleep(3)  # Sleep for 3 seconds before the next iteration

        except Exception as e:
            print(f"Error in initial waiting loop: {e}")
            time.sleep(3)  # Sleep for 3 seconds and retry

if __name__ == "__main__":
    initial_waiting_loop_sell()
