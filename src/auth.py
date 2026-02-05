import asyncio
import os

from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, PartialCreateOrderOptions, BookParams
from py_clob_client.exceptions import PolyApiException
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL


load_dotenv()


async def main():
    # L1 wallet authentication
    host = "https://clob.polymarket.com"
    chain_id = 137  # Polygon mainnet
    private_key = os.getenv("private_key")

    # client = ClobClient(
        # host=host,
        # chain_id=chain_id,
        # key=private_key  # Signer enables L1 methods
    # )

    # print(f"L1 client created: \n{client}")
    # Gets API key, or else creates
    # api_creds = await client.create_or_derive_api_creds()
    # Client expects ApiCreds (object with .api_key, .api_secret, .api_passphrase), not a dict
    api_creds = ApiCreds(
        api_key=os.getenv("api_key"),
        api_secret=os.getenv("api_secret"),
        api_passphrase=os.getenv("api_passphrase"),
    )

    # api_creds = {
    #     "apiKey": "550e8400-e29b-41d4-a716-446655440000",
    #     "secret": "base64EncodedSecretString",
    #     "passphrase": "randomPassphraseString"
    # }

    print(f"API credentials: \n{api_creds}")

    # L2 wallet authentication
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137,
        key=os.getenv("private_key"),
        creds=api_creds,  # Use the credentials from L1 auth (dict above), not an env var
        signature_type=2,  # signatureType explained below 0: EOA metamask, 1: wallet in polymarket
        funder=os.getenv("founder_address")  # funder explained below
    )
    print(f"L2 client created: \n{client}\n\n")

    # Get market info first or take from the copy trade script
    market = client.get_market(condition_id)
    print(market)
    
    response = client.create_and_post_order(
        OrderArgs(
            token_id="TOKEN_ID",
            price=0.50,       # Price per share ($0.50)
            size=10,          # Number of shares
            side=BUY,         # BUY or SELL
        ),
        options={
            "tick_size": market["tickSize"],
            "neg_risk": market["negRisk"],    # True for multi-outcome events
        },
        order_type=OrderType.GTC  # Good-Til-Cancelled
    )

    print("Order ID:", response["orderID"])
    print("Status:", response["status"])

    # View all open orders
    open_orders = client.get_open_orders()
    print(f"You have {len(open_orders)} open orders")

    # View your trade history
    trades = client.get_trades()
    print(f"You've made {len(trades)} trades")

    # Cancel an order
    client.cancel_order(response["orderID"])

    # market = client.get_market(conditioId)
    # print(market)
    # print(market.token_id)

    # token_id = "87952206431192442877086025502136777600339876380657249548747104885754218775925"  # Get a token ID: https://docs.polymarket.com/developers/gamma-markets-api/get-markets

    # mid = client.get_midpoint(token_id)
    # price = client.get_price(token_id, side="BUY")
    # book = client.get_order_book(token_id)
    # books = client.get_order_books([BookParams(token_id=token_id)])
    # print(mid, price, book.market, len(books))

    # mo = MarketOrderArgs(token_id="87952206431192442877086025502136777600339876380657249548747104885754218775925", amount=25.0, side=BUY, order_type=OrderType.FOK)  # Get a token ID: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
    # signed = client.create_market_order(mo)
    # resp = client.post_order(signed, OrderType.FOK)
    # print("Market order placed:", resp)

if __name__ == "__main__":
    asyncio.run(main())