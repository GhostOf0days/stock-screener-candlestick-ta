import yfinance as yf
import os,csv
import pandas as pd
import talib
from flask import Flask, render_template, request
from patterns import patterns
from datetime import date
app = Flask(__name__)

@app.route('/snapshot')
def snapshot():
    todays_date = date.today()
    with open("datasets/companies.csv") as f:
        for line in f:
            if "," not in line:
                continue
            stock_ticker=line.strip().split(",")[0]
            data = yf.download(stock_ticker, start="{}-01-01".format(todays_date.year),
                               end="{}-{}-{}".format(todays_date.year, todays_date.month, todays_date.day))
            print(data)
            data.to_csv('datasets/daily/{}.csv'.format(stock_ticker))
    return {'code': 'success'}

@app.route('/')
def index():
    pattern = request.args.get('pattern',False)
    stocks = {}
    with open("datasets/companies.csv") as f:
        for company_info in csv.reader(f):
            stocks[company_info[0]] = {"company": company_info[1]}
    if pattern:
        for dataset in os.listdir('datasets/daily'):
            df = pd.read_csv('datasets/daily/{}'.format(dataset))
            pattern_func=getattr(talib,pattern)
            symbol=dataset.split('.')[0]
            try:
                result=pattern_func(df['Open'],df['High'],df['Low'],df['Close'])
                last = result.tail(1).values[0]
                if last > 0:
                    stocks[symbol][pattern] = "Bullish"
                elif last < 0:
                    stocks[symbol][pattern] = "Bearish"
                else:
                    stocks[symbol][pattern] = None
            except Exception as e:
                print('Failed on Dataset: ', dataset)
    return render_template('index.html', patterns=patterns, stocks=stocks, pattern=pattern)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)