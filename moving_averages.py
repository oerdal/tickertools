from flask import Flask, redirect, url_for, render_template
from datetime import date, datetime, time, timedelta, timezone
from pytz import utc
from dotenv import load_dotenv
import finnhub, pytz
import time as tm
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import json, os

load_dotenv()
api_key = os.getenv("API_KEY")
finnhub_client = finnhub.Client(api_key=api_key)

app = Flask(__name__)

def summarize_ticker(sym):
    UTC_now = datetime.now(utc)
    EST_now = datetime.now(pytz.timezone('US/Eastern'))
    if UTC_now.date() == EST_now.date():
        market_open = (datetime.combine(UTC_now.date(),time(9,30)) - EST_now.utcoffset())
        market_close = market_open + timedelta(hours=6,minutes=30)
        open_time = int(market_open.replace(tzinfo=timezone.utc).timestamp())
        close_time = int(market_close.replace(tzinfo=timezone.utc).timestamp())
        current_time = int(tm.time())

        res = finnhub_client.stock_candles(sym, '1', open_time, min(close_time, current_time))
        return res

# step ex: 50, 100, 200 day
def simple_moving_average(df, x='t', y='c'):
    steps = [10, 50, 100, 200]
    data_pts = df.shape[0]
    SMAs = []

    for step in steps:
        SMA = {}
    
        for i in range(0,data_pts-step):
            avg = df['c'].iloc[i:i+step].mean()
            SMA[df['t'].iloc[i+step]] = avg
        SMAs.append(SMA)
    
    return SMAs

def ticker_data(sym):
    end_dt = datetime.now(utc)
    start_dt = end_dt - timedelta(days=800)
    start_time = str(int(start_dt.replace(tzinfo=timezone.utc).timestamp()))
    end_time = str(int(end_dt.replace(tzinfo=timezone.utc).timestamp()))

    try:
        res = finnhub_client.stock_candles(sym, 'D', start_time, end_time)
        if res['s'] == 'ok':
            return pd.DataFrame(res)
        elif res['s'] == 'no_data':
            return pd.DataFrame({})
        else:
            return None
    except:
        return None

def create_plot(df):
    df['dt'] = df['t'].apply(lambda t : datetime.fromtimestamp(t))

    data = [
        go.Scatter(
            x=df['dt'],
            y=df['c'],
            mode='markers',
            name='close price',
            marker=dict(
                size=3,
                color=df['v'],
                colorbar=dict(title='Trading Volume'),
                colorscale='Inferno'
            )
        )
    ]
    
    SMAs = simple_moving_average(df)
    steps = [10, 50, 100, 200]
    for i in range(len(SMAs)):
        srs = pd.Series(data=SMAs[i].values(), index=[datetime.fromtimestamp(t) for t in SMAs[i].keys()])
        data.append(go.Scatter(
            x=srs.index,
            y=srs.values,
            mode='lines',
            name=str(steps[i]) + ' day SMA',
        ))

    print(data)

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<exch>/')
def exchange(exch):
    if exch in ['GSPC','NDX','DJI']:
        syms = finnhub_client.indices_const(symbol = '^' + exch)['constituents']
        syms.sort()
        return render_template('exchange.html', exch=exch, syms=syms)
    else:
        return redirect(url_for('home'))

@app.route('/<path:exch>/<sym>')
def ticker(exch, sym):
    df = ticker_data(sym)
    if df is None:
        return 'Invalid Ticker or Server Error'
    else:
        if df.empty:
            return 'No data available'
        else:
            scatter = create_plot(df)
            return render_template('graph.html', plot=scatter, sym=sym)

if __name__ == '__main__':
    app.run(debug=True)