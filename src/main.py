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

# fetch the target wallet's open positions
last_ts = 0

def fetch_trades(user: str, limit: int = 50):
    params = {"user": user, "limit": limit}
    r = requests.get(f"{data_api}/trades", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_positions(user: str, limit: int = 1):
    params = {"user": user, "limit": limit}
    r = requests.get(f"{data_api}//activity?limit=100&sortBy=TIMESTAMP&sortDirection=DESC&user={target_wallet}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_total_value(user: str, limit: int = 1):
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
            ts = int(t["timestamp"])
            side = t.get("side")
            condition_id = t.get("conditionId")
            price = t.get("price")
            size = t.get("size")
            title = t.get("title")
            outcome = t.get("outcome")
            tx = t.get("transactionHash")

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