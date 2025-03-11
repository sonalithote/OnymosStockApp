Stock trading engine that matches Buy and Sell orders for multiple tickers.
"""
 Order class: Represents a single stock order (Buy/Sell)
 Attributes: order_type, ticker, quantity, price, next (for linked list)

 StockTradingEngine class:
 - Manages array of linked lists (order_books) for up to 1024 tickers
 - Uses locks to handle race conditions

 add_order method:
 - Adds new Order to linked list for a ticker
 - Calls match_order after adding

 match_order method:
 - Matches Buy and Sell orders (Buy price >= lowest Sell price)
 - Uses temporary lists to sort and process matches
 - Rebuilds linked list with unmatched orders

 simulate_trading function:
 - Creates threads to generate random Buy/Sell orders
 - Simulates real-time trading activity

 Concurrency:
 - Uses threading and locks for thread-safe operations
"""
