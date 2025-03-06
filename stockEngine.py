# Stock trading engine that matches Buy and Sell orders for multiple tickers.
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

import threading
import random
import time

class Order:
    def __init__(self, order_type, ticker, quantity, price):
        self.order_type = order_type  # "Buy" or "Sell"
        self.ticker = ticker          # Stock ticker symbol
        self.quantity = quantity      # Number of shares
        self.price = price            # Price per share
        self.next = None              # Pointer to the next order in the linked list

class StockTradingEngine:
    def __init__(self):
        self.MAX_TICKERS = 1024
        self.order_books = [None] * self.MAX_TICKERS  # Array of linked lists for each ticker
        self.locks = [threading.Lock() for _ in range(self.MAX_TICKERS)]  # Locks for each ticker's order book

    def _get_ticker_index(self, ticker):
        """Hash the ticker symbol to an index."""
        return hash(ticker) % self.MAX_TICKERS

    def add_order(self, order_type, ticker, quantity, price):
        """Add a new order to the order book."""
        index = self._get_ticker_index(ticker)
        new_order = Order(order_type, ticker, quantity, price)

        with self.locks[index]:  # Lock the order book for this ticker
            if not self.order_books[index]:
                self.order_books[index] = new_order
            else:
                current = self.order_books[index]
                while current.next:
                    current = current.next
                current.next = new_order

        print(f"Added {order_type} order: {ticker}, Quantity: {quantity}, Price: {price}")
        self.match_order(index)

    def match_order(self, index):
        """Match Buy and Sell orders for a specific ticker."""
        with self.locks[index]:  # Lock the order book for this ticker
            buy_orders = []  # Temporary list to hold Buy orders
            sell_orders = []  # Temporary list to hold Sell orders

            # Split orders into Buy and Sell lists
            current = self.order_books[index]
            while current:
                if current.order_type == "Buy":
                    buy_orders.append(current)
                elif current.order_type == "Sell":
                    sell_orders.append(current)
                current = current.next

            # Sort Buy orders by descending price and Sell orders by ascending price
            buy_orders.sort(key=lambda x: -x.price)
            sell_orders.sort(key=lambda x: x.price)

            i, j = 0, 0
            while i < len(buy_orders) and j < len(sell_orders):
                buy_order = buy_orders[i]
                sell_order = sell_orders[j]

                if buy_order.price >= sell_order.price:  # Match condition
                    traded_quantity = min(buy_order.quantity, sell_order.quantity)
                    print(f"Matched: {buy_order.ticker} - {traded_quantity} shares at ${sell_order.price}")

                    buy_order.quantity -= traded_quantity
                    sell_order.quantity -= traded_quantity

                    if buy_order.quantity == 0:
                        i += 1  # Move to the next Buy order
                    if sell_order.quantity == 0:
                        j += 1  # Move to the next Sell order
                else:
                    break

            # Rebuild the linked list with remaining unmatched orders
            remaining_orders = buy_orders[i:] + sell_orders[j:]
            head = None
            for order in reversed(remaining_orders):  # Rebuild in reverse to maintain order
                order.next = head
                head = order

            self.order_books[index] = head

def simulate_trading():
    engine = StockTradingEngine()
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    order_types = ["Buy", "Sell"]

    def random_trading():
        while True:
            ticker = random.choice(tickers)
            order_type = random.choice(order_types)
            quantity = random.randint(1, 100)
            price = round(random.uniform(50.0, 1500.0), 2)
            engine.add_order(order_type, ticker, quantity, price)
            time.sleep(random.uniform(0.1, 1.0))  # Simulate delay between trades

    threads = []
    for _ in range(5):  # Simulate multiple brokers adding orders concurrently
        thread = threading.Thread(target=random_trading)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    simulate_trading()