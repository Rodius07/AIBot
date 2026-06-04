from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv('keys.env')

API_KEY = os.getenv('bybitapi')
API_SECRET = os.getenv('bybitapis')

def round_qty(symbol, qty):
    if "BTC" in symbol:
        return round(qty, 3)
    elif "ETH" in symbol:
        return round(qty, 2)
    elif "XRP" in symbol or "DOGE" in symbol:
        return round(qty, 1)
    else:
        return round(qty, 1)
def place_order(operation_type, usdt_amount, take_profit, stop_loss, symbol, order_type="Limit", price=None):

    client = HTTP(
        testnet=False,
        api_key=API_KEY,
        api_secret=API_SECRET
    )

    price_act = client.get_tickers(
        category="linear",
        symbol=symbol,
    )
    qty = round_qty(symbol, usdt_amount / float(price_act['result']['list'][0]['lastPrice']))

    response = client.place_order(
        category="linear",
        symbol=symbol,
        side=operation_type,
        order_type=order_type,
        qty=str(qty),
        price=str(price) if order_type == "Limit" else None,
        time_in_force="GTC",
        take_profit=str(take_profit),
        stop_loss=str(stop_loss),
        tp_trigger_by="LastPrice",
        sl_trigger_by="LastPrice"
    )
    print(response)

    return "Успешно"


def cancel_order_partial(symbol: str):
    client = HTTP(
        testnet=False,
        api_key=API_KEY,
        api_secret=API_SECRET
    )

    active_orders = client.get_open_orders(category="linear", symbol=symbol)
    orders = active_orders.get('result', {}).get('list', [])

    if not orders:
        return "Нет активных ордеров для отмены."

    cancelled = []
    for order in orders:
        resp = client.cancel_order(
            category="linear",
            symbol=symbol,
            order_id=order["orderId"]
        )
        cancelled.append(resp)

    return "Успешно"
