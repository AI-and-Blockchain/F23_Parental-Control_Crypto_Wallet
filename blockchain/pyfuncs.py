import requests
from bs4 import BeautifulSoup

def getLastTrans(addr):
    url = f'https://mumbai.polygonscan.com/address/{addr}'# + addr
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        targ = soup.find(class_='myFnExpandBox_searchVal')

        if targ:
            return targ.text
        else:
            print("Element not found.")
    else:
        print(f"Failed to retrieve the web page. Status code: {response.status_code}")



def MATICtoETH(MATICAMT):
    resp = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY=dc0ab239-8691-42c2-823d-b230fc37d488&convert=MATIC')
    data = resp.json()
    MATICperETH = -1

    for entry in data['data']:
        if "symbol" in entry and entry["symbol"] == "ETH":
            MATICperETH = entry['quote']['MATIC']['price']
            break

    if (MATICperETH == -1): return -1
    return str(MATICAMT / MATICperETH)
