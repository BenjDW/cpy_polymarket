from py_clob_client.client import ClobClient
from dotenv import load_dotenv
import os, requests, asyncio, time

# for the metamask wallet
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")
public_key = os.getenv("PUBLIC_KEY")
api_key = os.getenv("API_KEY")

# target wallet
target_wallet = os.getenv("target_wallet")

# polymarket api
data_api = "https://data-api.polymarket.com"

client = ClobClient("https://clob.polymarket.com")  # Level 0 (no auth)

ok = client.get_ok()
server_time = client.get_server_time()
print(ok, server_time, "test client\n\n")


def buy_market(market_id: str, size: int, price: float):
    """
    Buy a market at a specific price and size.
    """
    client.buy_market(market_id, size, price)


def sell_market(market_id: str, size: int, price: float):
    """
    Sell a market at a specific price and size.
    """
    client.sell_market(market_id, size, price)


def cancel_order(order_id: str):
    """
    Cancel an order by its ID.
    """
    client.cancel_order(order_id)


def get_order_status(order_id: str):
    """
    Get the status of an order by its ID.
    """
    return client.get_order_status(order_id)


def buy_limit(market_id: str, size: int, price: float):
    """
    Buy a market at a specific price and size.
    """
    client.buy_limit(market_id, size, price)


def sell_limit(market_id: str, size: int, price: float):
    """
    Sell a market at a specific price and size.
    """
    client.sell_limit(market_id, size, price)

def cancel_limit(order_id: str):
    """
    Cancel a limit order by its ID.
    """
    client.cancel_limit(order_id)

def get_limit_order_status(order_id: str):
    """
    Get the status of a limit order by its ID.
    """
    return client.get_limit_order_status(order_id)




# fetch the target wallet's open positions
last_ts = 0

def fetch_trades(user: str, limit: int = 50):
    """
    Fetch trade history for a Polymarket user.
    Returns list of trade objects; each trade has:
      - timestamp: Unix time of the trade
      - side: "BUY" or "SELL"
      - conditionId: unique market id
      - price: price PER SHARE (0–1). Cost to buy 1 share of that outcome (e.g. 0.65 = 65¢ per share)
      - size: number of shares traded
      - title: market question text
      - outcome: "Yes" or "No" (which outcome was traded)
      - transactionHash: on-chain tx hash
    """
    params = {"user": user, "limit": limit}
    r = requests.get(f"{data_api}/trades", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_positions(user: str, limit: int = 1):
    """
    Fetch activity/positions for a Polymarket user (recent activity, sorted by time).
    Returns activity data: positions, orders, and related market info.
    """
    params = {"user": user, "limit": limit}
    r = requests.get(f"{data_api}//activity?limit=100&sortBy=TIMESTAMP&sortDirection=DESC&user={target_wallet}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_total_value(user: str, limit: int = 1):
    """
    Fetch total portfolio value for a Polymarket user (USD value of all open positions).
    Returns value data (e.g. total value in dollars).
    """
    params = {"user": user, "limit": limit}
    r = requests.get(f"{data_api}/value", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

print("fetching trades...\n")

for _ in range(1):
    try:
        trades = fetch_trades(target_wallet, limit=50)

        new = [t for t in trades if int(t.get("timestamp", 0)) > last_ts]
        new.sort(key=lambda t: int(t.get("timestamp", 0)))

        # pour remetre en boucle, sans le [-1]
        #for t in new:
        if new:
            t = new[-1]
            ts = int(t["timestamp"])           # Unix time of the trade
            side = t.get("side")                # "BUY" or "SELL"
            condition_id = t.get("conditionId") # Unique market id
            price = t.get("price")              # Price per share (0–1): cost to buy 1 share of that outcome
            size = t.get("size")                # Number of shares traded
            title = t.get("title")              # Market question text
            outcome = t.get("outcome")          # "Yes" or "No" (which outcome)
            tx = t.get("transactionHash")      # On-chain transaction hash

            print(f"[{ts}] {side} {size}@{price} | {outcome} | {title} | market={condition_id} | tx={tx} \n")
            last_ts = max(last_ts, ts)

        time.sleep(1.0)

    except Exception as e:
        print("ERR:", e)
        time.sleep(2.0)

print("fetching activity...\n")

for _ in range(1):
    try:
        positions = fetch_positions(target_wallet, limit=1)
        print(positions, "\n")
        value = fetch_total_value(target_wallet, limit=1)
        print("total value position open:\n", value)
    except Exception as e:
        print("ERR:", e)
        time.sleep(2.0)