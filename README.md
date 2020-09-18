# tickertools
lightweight flask app for investment related widgets or tools


TODO: remove env and use requirements.txt in future deploy


## external tools
data from finnhub.io api

plotting done using plotly in python and javascript


## usage
from flask official docs

powershell
```powershell
$env:FLASK_APP="moving_averages.py"
flask run
```

command prompt
```shell
set FLASK_APP=moving_averages.py
flask run
```

bash
```shell
export FLASK_APP=moving_averages.py
flask run
```

select from a popular US exchange and view stock info from any of the listed tickers

#### current info includes:
* medium term closing prices
* 10, 50, 100, and 200 day simple moving averages
