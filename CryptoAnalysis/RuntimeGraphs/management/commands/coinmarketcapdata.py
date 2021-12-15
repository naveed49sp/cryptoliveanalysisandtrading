from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pprint
import os

import csv

pp = pprint.PrettyPrinter(indent=4)


symbolstr=','.join(('BTC,ETH,BNB,XRP,USDT,ADA,DOT,UNI,LTC,LINK,XLM,BCH', 
        'THETA,FIL,USDC,TRX,DOGE,WBTC,VET,SOL,KLAY,EOS,XMR,LUNA', 
        'MIOTA,BTT,CRO,BUSD,FTT,AAVE,BSV,XTZ,ATOM,NEO,AVAX,ALGO', 
        'CAKE,HT,EGLD,XEM,KSM,BTCB,DAI,HOT,CHZ,DASH,HBAR,RUNE,MKR,ZEC',
        'ENJ,DCR,MKR,ETC,GRT,COMP,STX,NEAR,SNX,ZIL,BAT,LEO,SUSHI,ROSE'))

symbol_list=symbolstr.split(',')


url= f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
print(url)
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': "4e03c3c4-2d11-4e3b-821a-c03f13997b3b",
}
parameters = {
  'symbol':symbolstr
  }
session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

except (ConnectionError, Timeout, TooManyRedirects) as e:
    data = json.loads(response.text)

pp.pprint(data)
file_to_open='coinmap.txt'
line_list=[]
with open(file_to_open, 'w') as this_csv_file:
  
    for symbol in symbol_list:
        
        thename=data['data'][symbol]['name']
        cid=data['data'][symbol]['id']
        quote=data['data'][symbol]['quote']

        line=f'{cid}, {thename}, {symbol},{quote}'
        line_list.append(line)

    for line in line_list:
        this_csv_file.write(line)
        this_csv_file.write('\n')