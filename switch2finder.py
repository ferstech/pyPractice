import requests
from bs4 import BeautifulSoup

# URLs for Nintendo Switch 2 product pages (update these as needed)
RETAILERS = {
    'BestBuy': 'https://www.bestbuy.com/site/searchpage.jsp?st=switch+2',
    'Walmart': 'https://www.walmart.com/search/?query=switch%202',
    'GameStop': 'https://www.gamestop.com/search/?q=switch%202',
}

def check_bestbuy(url):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Look for 'Sold Out' or 'Add to Cart' button
    if 'Sold Out' in resp.text:
        return 'Sold Out'
    elif 'Add to Cart' in resp.text:
        return 'Available!'
    return 'Check manually'

def check_walmart(url):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    if 'Out of stock' in resp.text:
        return 'Out of Stock'
    elif 'Add to cart' in resp.text:
        return 'Available!'
    return 'Check manually'

def check_gamestop(url):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    if 'Not Available' in resp.text or 'Out of Stock' in resp.text:
        return 'Out of Stock'
    elif 'Add to Cart' in resp.text or 'Pick Up Today' in resp.text:
        return 'Available!'
    return 'Check manually'

if __name__ == '__main__':
    print('Checking Nintendo Switch 2 availability:')
    print('-' * 40)
    print(f"BestBuy:   {check_bestbuy(RETAILERS['BestBuy'])} ({RETAILERS['BestBuy']})")
    print(f"Walmart:   {check_walmart(RETAILERS['Walmart'])} ({RETAILERS['Walmart']})")
    print(f"GameStop:  {check_gamestop(RETAILERS['GameStop'])} ({RETAILERS['GameStop']})")
