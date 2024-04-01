from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


def getCoinPrice(Cryptocurrency):
  headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'ef324c65-c89e-4243-835f-ca167f5e9b1e',
  'X-CMC_PRO_API_KEY': os.environ['coinMarket_ACCESS_TOKEN'],
  }
  session = Session()
  session.headers.update(headers)
  
  try:
    parameters = {'slug' : Cryptocurrency}

    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    #btcPrice = data['data']['1']['quote']['USD']['price']
    #ethPrice = data['data']['1027']['quote']['USD']['price']
 
    #ssvPrice = data['data']['12999']['quote']['USD']['price']

    price = list(data['data'].items())[0][1]['quote']['USD']['price']

    
    return price

  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

def getCoinDetails(Cryptocurrency):
  headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.environ['coinMarket_ACCESS_TOKEN'],
  }
  session = Session()
  session.headers.update(headers)
  
  try:
    parameters = {'slug' : Cryptocurrency}

    response = session.get(url, params=parameters)
    data = json.loads(response.text)

   
    return data

  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

