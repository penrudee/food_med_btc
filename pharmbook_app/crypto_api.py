import requests
from flask import current_app
from flask_caching import Cache
from pharmbook_app import pharmbook_init
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(pharmbook_init)

@cache.memoize(timeout=300)
def get_btc_thb_rate():
    """ดึงอัตราแลกเปลี่ยน BTC/THB ล่าสุด"""
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=thb'
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['bitcoin']['thb']
    except Exception as e:
        current_app.logger.error(f"Error fetching BTC rate: {e}")
        return None
@cache.memoize(timeout=300)
def get_btc_trend():
    """ตรวจสอบแนวโน้มราคา BTC ใน 24 ชั่วโมง"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=thb&days=1'
        response = requests.get(url, timeout=5)
        prices = response.json()['prices']
        
        if len(prices) >= 2:
            old_price = prices[0][1]
            new_price = prices[-1][1]
            if new_price > old_price:
                return 'up'
            elif new_price < old_price:
                return 'down'
        return 'stable'
    except Exception as e:
        current_app.logger.error(f"Error fetching BTC trend: {e}")
        return 'stable'