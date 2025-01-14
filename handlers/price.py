
import requests

def get_token_price(symbol):
    url = f"https://www.mexc.com/open/api/v2/market/ticker?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    if data and 'data' in data and len(data['data']) > 0:
        price = data['data'][0]['last']
        return price
    else:
        return "Price data not available"
        