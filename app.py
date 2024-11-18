from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime as dt  
# from flask_cors import CORS
import flask
def ts_time(ts):
    if len(str(ts)) ==13:
        ts = ts/1000
    from datetime import datetime,timezone 
    return datetime.strftime(datetime.fromtimestamp(ts,timezone.utc), '%Y-%m-%d %H:%M:%S')
# print(flask.__version__)

def create_app():
    app = Flask(__name__)
    # CORS(app)  # 启用 CORS

    binance_data = []
    binance_spot_data = []
    bitget_data = []
    okx_data = []
    bybit_data = []
    kucoin_data = []
    gateio_data = []
    huobi_data = []
    mxc_data = []

    # @app.before_app_first_request
    def load_binance_info():
        '''binance exchange info'''
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        data = [x for x in requests.get(url).json()['symbols'] if x['status'] == 'TRADING']
        for symbol in data:
            temp = {
                'base_asset': symbol['baseAsset'],
                'quote_asset': symbol['quoteAsset'],
                'symbol': symbol['symbol']
            }
            binance_data.append(temp)

        bitget_url = 'https://api.bitget.com/api/v2/spot/public/symbols'
        bitget_data = [{'base_asset': x['baseCoin'], 'quote_asset': x['quoteCoin'], 'symbol': x['symbol']} for x in requests.get(bitget_url).json()['data']]
        bitget_data = bitget_data
    
    def load_binanceSpot_info():
        '''binance exchange info'''
        url = "https://api.binance.com/api/v3/exchangeInfo"
        data = [x for x in requests.get(url).json()['symbols'] if x['status'] == 'TRADING']
        for symbol in data:
            temp = {
                'base_asset': symbol['baseAsset'],
                'quote_asset': symbol['quoteAsset'],
                'symbol': symbol['symbol']
            }
            binance_spot_data.append(temp)

    

    def load_bitget_info():
        url = "https://api.bitget.com/api/v2/spot/public/symbols"
        data = requests.get(url).json()['data']
        for symbol in data:
            temp = {'base_asset': symbol['baseCoin'],
                    'quote_asset': symbol['quoteCoin'],
                    'symbol': symbol['symbol']
                    }
            bitget_data.append(temp)

    def load_bybit_info():
        url = "https://api.bybit.com/v5/market/instruments-info?category=spot"
        try:
            data = requests.get(url).json()['result']['list']
            for symbol in data:
                temp = {'base_asset': symbol['baseCoin'],
                        'quote_asset': symbol['quoteCoin'],
                        'symbol': symbol['symbol']
                        }
                bybit_data.append(temp)
        except Exception as e:
            return bybit_data

    def load_okx_info():
        url = 'https://www.okx.com/api/v5/public/instruments?instType=SPOT'
        data = requests.get(url).json()['data']
        for symbol in data:
            if symbol['instId'] != 'ZRO-USDT':
                temp = {'base_asset': symbol['baseCcy'],
                        'quote_asset': symbol['quoteCcy'],
                        'symbol': symbol['instId']
                        }
                okx_data.append(temp)

    def load_kucoin_info():
        url = "https://api.kucoin.com/api/v2/symbols"
        data = [x for x in requests.get(url).json()['data'] if x['enableTrading'] == True]
        for symbol in data:
            temp = {'base_asset': symbol['baseCurrency'],
                    'quote_asset': symbol['quoteCurrency'],
                    'symbol': symbol['symbol']
                    }
            kucoin_data.append(temp)

    def load_gateio_info():
        url = "https://api.gateio.ws/api/v4/spot/currency_pairs"
        data = [x for x in requests.get(url).json() if x['trade_status'] == 'tradable']
        for symbol in data:
            temp = {'base_asset': symbol['base'],
                    'quote_asset': symbol['quote'],
                    'symbol': symbol['id']
                    }
            gateio_data.append(temp)

    def load_huobi_info():
        url = 'https://api.huobi.pro/v2/settings/common/symbols'
        data = [x for x in requests.get(url).json()['data'] if x['state'] == 'online']
        for symbol in data:
            temp = {'base_asset': symbol['bcdn'],
                    'quote_asset': symbol['qcdn'],
                    'symbol': symbol['dn']
                    }
            huobi_data.append(temp)

    def load_mxc_info():
        url = 'https://api.mexc.com/api/v3/exchangeInfo'
        data = [x for x in requests.get(url).json()['symbols'] if x['status'] == '1']
        for symbol in data:
            temp = {'base_asset': symbol['baseAsset'],
                    'quote_asset': symbol['quoteAsset'],
                    'symbol': symbol['symbol']
                    }
            mxc_data.append(temp)

    load_binance_info()
    load_bitget_info()
    load_bybit_info()
    load_okx_info()
    load_kucoin_info()
    load_gateio_info()
    load_huobi_info()
    load_mxc_info()
    load_binanceSpot_info()

    @app.route('/')
    def index():
        return render_template('index.html', assets_data=binance_data)
    
    

    @app.route('/chart_data', methods=['POST','GET'])
    def chart_data():
        base_asset = request.form['base_asset']
        quote_asset = request.form['quote_asset']
        start_time = request.form['start_time']
        start_time = int(pd.to_datetime(start_time).timestamp() * 1000)
        end_time = request.form['end_time']
        end_time = int(pd.to_datetime(end_time).timestamp() * 1000)
        print('query startTime: ' + ts_time(start_time))
        print('query endTime: ' + ts_time(end_time))
        print('++++'*50)
        interval = request.form['interval']
        interval_bitget = {'1m': '1min', '5m': '5min'}[interval]
        interval_bybit = {'1m': '1', '5m': '5'}[interval]
        interval_kucoin = {'1m': '1min', '5m': '5min'}[interval]
        interval_huobi = {'1m': '1min', '5m': '5min'}[interval]

        def fetch_binance_data(base_asset,quote_asset, interval, start_time, end_time):
            
            # try:
            
            if '1000' in base_asset:
                binance_base_asset = base_asset.replace('1000','')
            else:
                binance_base_asset = base_asset
   
            symbol = binance_base_asset.upper()+quote_asset.upper()
            if symbol in [x['symbol'] for x in binance_spot_data]: 
                rename_columns = ['open_time','high','low','close']
                url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000"
                data = requests.get(url).json()
                print(url)
                try:
                    df = pd.DataFrame(data).iloc[:,[0,2,3,4]]
                    df.columns = rename_columns
                    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                    df[['close', 'high', 'low']] = df[['close', 'high', 'low']].astype(float)
                    if '1000' in base_asset.upper():
                        df['close'] = df['close']*1000
                        df['high'] = df['high']*1000
                        df['low'] = df['low']*1000
                    return df
                except Exception as e:
                    print(e)
                    print(requests.get(url))
            else:
                df = pd.DataFrame(columns =['open_time','high','low','close'])
                return df 

        def fetch_binanceFutures_data(exchange,base_asset,quote_asset, interval, start_time, end_time):
        
            try:
                symbol = base_asset.upper() + quote_asset.upper()
                rename_columns = ['open_time','high','low','close']
                binance_url_dict = {
                'binance_index': f"https://fapi.binance.com/fapi/v1/indexPriceKlines?pair={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000",
                'binance_futures':f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000",
                'binance_markprice': f"https://fapi.binance.com/fapi/v1/markPriceKlines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000"
            }
                # url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000"
                print(binance_url_dict[exchange])

                data = requests.get(binance_url_dict[exchange]).json()
                df = pd.DataFrame(data).iloc[:,[0,2,3,4]]
                df.columns = rename_columns
                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
                df[['close', 'high', 'low']] = df[['close', 'high', 'low']].astype(float)
                return df
            except Exception as e:
                print(e)
        

        df_binance = fetch_binance_data(
            base_asset,
            quote_asset,
            interval,
            start_time,
            end_time,
        )

        df_binance_index = fetch_binanceFutures_data(
            'binance_index',
            base_asset,
            quote_asset,
            interval,
            start_time,
            end_time,
        )

        df_binance_futures = fetch_binanceFutures_data(
            'binance_futures',
            base_asset,
            quote_asset,
            interval,
            start_time,
            end_time,
        )

        df_binance_markPrice = fetch_binanceFutures_data(
            'binance_markprice',
            base_asset,
            quote_asset,
            interval,
            start_time,
            end_time,
        )

            # Bitget data fetch
        if '1000' in base_asset:
            bitget_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            bitget_base_asset = 'BABYDOGE'
        else:
            bitget_base_asset = base_asset
        bitget_symbol = bitget_base_asset + quote_asset
        if bitget_symbol in [x['symbol'] for x in bitget_data]:
            minute = 1000*60 
            if (end_time - start_time)/minute > 1000 and interval_bitget =='1min':
                end_time = start_time + minute*999
                url_bitget = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={bitget_symbol}&granularity={interval_bitget}&startTime={start_time-1000}&endTime={end_time}&limit=1000"
                
            else:
                url_bitget = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={bitget_symbol}&granularity={interval_bitget}&startTime={start_time-1000}&endTime={end_time}&limit=1000"
            print(url_bitget)
            data_bitget = requests.get(url_bitget).json()['data']
            df_bitget = pd.DataFrame(data_bitget, columns=['open_time', 'open', 'high', 'low', 'close', 'volume','unknown_1','unknown_2'])
            df_bitget = df_bitget[['open_time','high','low','close']]
            df_bitget[['high','low','close']] = df_bitget[['high','low','close']].astype(float)
            df_bitget['open_time'] = pd.to_datetime(df_bitget['open_time'].astype(int), unit='ms')
            df_bitget = df_bitget.sort_values(by='open_time')
            if '1000' in base_asset:
                df_bitget['close'] = df_bitget['close']*1000
                df_bitget['high'] = df_bitget['high']*1000
                df_bitget['low'] = df_bitget['low']*1000
            elif base_asset == '1MBABYDOGE':
                df_bitget['close'] = df_bitget['close']*1000000
                df_bitget['high'] = df_bitget['high']*1000000
                df_bitget['low'] = df_bitget['low']*1000000
        else:
            df_bitget = pd.DataFrame(columns =['open_time', 'open', 'high', 'low', 'close', 'volume','unknown_1','unknown_2'] )

        # Kucoin data fetch 
        if '1000' in base_asset:
            kucoin_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            kucoin_base_asset = 'BABYDOGE'
        else:
            kucoin_base_asset = base_asset
        kucoin_symbol = kucoin_base_asset + '-'+ quote_asset
        if kucoin_symbol in [x['symbol'] for x in kucoin_data]:
            minute = 1000*60 

            if (end_time - start_time)/minute > 1000 or interval_kucoin =='1min':
                end_time = start_time + minute*999
                url = f"https://api.kucoin.com/api/v1/market/candles?type={interval_kucoin}&symbol={kucoin_symbol}&startAt={int(start_time/1000)}&endAt={int(end_time/1000)}"
                print('1min: '+url)
           
            else:
                print(interval_kucoin)
                url = f"https://api.kucoin.com/api/v1/market/candles?type={interval_kucoin}&symbol={kucoin_symbol}&startAt={int(start_time/1000)}&endAt={int(end_time/1000)}"
                print('5min: '+url)
     
            print(url)
            try:
                df_kucoin = pd.DataFrame(requests.get(url).json()['data'])
                df_kucoin[0] = pd.to_datetime(df_kucoin[0].astype(int),unit='s')
                df_kucoin = df_kucoin.iloc[:,[0,2,3,4]]
                df_kucoin[2] = df_kucoin[2].astype(float)
                df_kucoin.columns = ['open_time','close','high','low']
                df_kucoin.sort_values(by='open_time',inplace=True)
                if '1000' in base_asset:
                    df_kucoin['close'] = df_kucoin['close']*1000
                    df_kucoin['high'] = df_kucoin['high']*1000
                    df_kucoin['low'] = df_kucoin['low']*1000
                elif base_asset == '1MBABYDOGE':
                    df_kucoin['close'] = df_kucoin['close']*1000000
                    df_kucoin['high'] = df_kucoin['high']*1000000
                    df_kucoin['low'] = df_kucoin['low']*1000000
            except Exception as e:
                print(url)
                df_kucoin = pd.DataFrame(columns = ['open_time','close','high','low'])
        else:
            df_kucoin = pd.DataFrame(columns = ['open_time','close','high','low'])

        # Gateio data fetch 
        if '1000' in base_asset:
            gateio_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            gateio_base_asset = 'BABYDOGE'
        else:
            gateio_base_asset = base_asset
        gateio_symbol = gateio_base_asset + '_'+ quote_asset
        if gateio_symbol in [x['symbol'] for x in gateio_data]:
            minute = 1000*60 

            if (end_time - start_time)/minute > 1000 and interval =='1m':
                end_time = start_time + minute*999
                url = f'https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={gateio_symbol}&interval={interval}&from={int(start_time/1000)}&to={int(end_time/1000)}&'
            else:
                url = f'https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={gateio_symbol}&interval={interval}&from={int(start_time/1000)}&to={int(end_time/1000)}&'

            print(url)
            try:
                df_gateio = pd.DataFrame(requests.get(url).json())
                df_gateio[0] = pd.to_datetime(df_gateio[0].astype(int),unit='s')
                df_gateio = df_gateio.iloc[:,[0,2,3,4]]
                df_gateio[2] = df_gateio[2].astype(float)
                df_gateio.columns = ['open_time','close','high','low']
                df_gateio.sort_values(by='open_time',inplace=True)
                if '1000' in base_asset:
                    df_gateio['close'] = df_gateio['close']*1000
                    df_gateio['high'] = df_gateio['high']*1000
                    df_gateio['low'] = df_gateio['low']*1000
                elif base_asset == '1MBABYDOGE':
                    df_gateio['close'] = df_gateio['close']*1000000
                    df_gateio['high'] = df_gateio['high']*1000000
                    df_gateio['low'] = df_gateio['low']*1000000
            except Exception as e:
                print(url)
                df_gateio = pd.DataFrame(columns = ['open_time','close'])
        else:
            df_gateio = pd.DataFrame(columns = ['open_time','close','high','low'])

        
        # Okx data fetch 
        if '1000' in base_asset:
            okx_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            okx_base_asset = 'BABYDOGE'
        else:
            okx_base_asset = base_asset
        okx_symbol = okx_base_asset + '-' + quote_asset
        okx_start = start_time
        
        if okx_symbol in [x['symbol'] for x in okx_data]:
            df_okx = pd.DataFrame()
            if interval == '1m':
                okx_time_step = 1000*60*100
            elif interval == '5m':
                okx_time_step = 1000 * 60 * 100*5
            try:
                while True:
                    url_okx = f"https://www.okx.com/api/v5/market/history-candles?instId={okx_symbol}&bar={interval}&after={(okx_start+okx_time_step)}&before={start_time}"
                    temp_df = pd.DataFrame(requests.get(url_okx).json()['data']).iloc[:,[0,2,3,4]]
                    df_okx = pd.concat(objs = [df_okx,temp_df],ignore_index=True)
                    okx_start = okx_start +okx_time_step
                    if okx_start >= end_time:
                        df_okx.columns = ['open_time','high','low','close']
                        df_okx[['high','low','close']] = df_okx[['high','low','close']].astype(float)
                        df_okx['open_time'] = pd.to_datetime(df_okx['open_time'].astype(int),unit='ms')
                        df_okx.drop_duplicates(inplace=True)
                        df_okx = df_okx.sort_values('open_time')
                        if '1000' in base_asset:
                            df_okx['close'] = df_okx['close']*1000
                            df_okx['high'] = df_okx['high']*1000
                            df_okx['low'] = df_okx['low']*1000
                        elif base_asset == '1MBABYDOGE':
                            df_okx['close'] = df_okx['close']*1000000
                            df_okx['high'] = df_okx['high']*1000000
                            df_okx['low'] = df_okx['low']*1000000
                        print(url_okx)
                        break 
            except Exception as e:
                print(e)
                print(url_okx)
        else:
            df_okx = pd.DataFrame(columns = ['open_time','high','low','close'])

        # Bybit data fetch
        if '1000' in base_asset:
            bybit_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            bybit_base_asset = 'BABYDOGE'
        else:
            bybit_base_asset = base_asset
        bybit_symbol = bybit_base_asset + quote_asset
        
        if bybit_symbol in [x['symbol'] for x in bybit_data]:
            print(bybit_symbol+'is in bybit' )
            minute = 1000*60 
            if (end_time - start_time)/minute > 1000 and interval_bybit=='1':
                end_time = start_time + minute*999
                url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={bybit_symbol}&interval={interval_bybit}&start={start_time}&end={end_time}&limit=1000"
            else:
                url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={bybit_symbol}&interval={interval_bybit}&start={start_time}&end={end_time}&limit=1000"
            print(url)
            try:
                df_bybit = pd.DataFrame(requests.get(url).json()['result']['list'])
                df_bybit[0] = pd.to_datetime(df_bybit[0].astype(int),unit='ms')
                df_bybit.sort_values(by=0,inplace=True)
                df_bybit = df_bybit.iloc[:,[0,2,3,4]]
                df_bybit.columns = ['open_time','high','low','close']
                df_bybit[['high','low','close']] = df_bybit[['high','low','close']].astype(float)
                if '1000' in base_asset:
                    df_bybit['close'] = df_bybit['close']*1000
                    df_bybit['high'] = df_bybit['high']*1000
                    df_bybit['low'] = df_bybit['low']*1000
                elif base_asset == '1MBABYDOGE':
                    df_bybit['close'] = df_bybit['close']*1000000
                    df_bybit['high'] = df_bybit['high']*1000000
                    df_bybit['low'] = df_bybit['low']*1000000

            except Exception as e:
                print(requests.get(url).status_code)
                df_bybit = pd.DataFrame(columns = ['open_time','high','low','close'])
        else:
            df_bybit = pd.DataFrame(columns = ['open_time','high','low','close'])

        # Huobi data fetch 
        if '1000' in base_asset:
            huobi_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            huobi_base_asset = 'BABYDOGE'
        else:
            huobi_base_asset = base_asset
        huobi_symbol = huobi_base_asset.lower()+ quote_asset.lower()
        if huobi_symbol in [x['symbol'].replace('/','').lower() for x in huobi_data]: 
            url = f"https://api.huobi.pro/market/history/kline?period={interval_huobi}&size=2000&symbol={huobi_symbol}"
            data = requests.get(url).json()['data']
            df_huobi = pd.DataFrame(data)
            df_huobi['id'] = pd.to_datetime(df_huobi['id'],unit='s')
            df_huobi = df_huobi[['id','high','low','close']]
            df_huobi.columns = ['open_time','high','low','close']
            df_huobi.sort_values(by='open_time',inplace=True)
            if '1000' in base_asset:
                df_huobi['close'] = df_huobi['close']*1000
                df_huobi['high'] = df_huobi['high']*1000
                df_huobi['low'] = df_huobi['low']*1000
            elif base_asset == '1MBABYDOGE':
                df_huobi['close'] = df_huobi['close']*1000000
                df_huobi['high'] = df_huobi['high']*1000000
                df_huobi['low'] = df_huobi['low']*1000000
        
        else:
            df_huobi = pd.DataFrame(columns = ['open_time','high','low','close'])

        # Mxc data fetch 
        if '1000' in base_asset:
            mxc_base_asset = base_asset.replace('1000','')
        elif base_asset == '1MBABYDOGE':
            mxc_base_asset = 'BABYDOGE'
        else:
            mxc_base_asset = base_asset
        mxc_symbol = mxc_base_asset + quote_asset
      
        if mxc_symbol in [x['symbol'] for x in mxc_data]:
            url = f"https://api.mexc.com/api/v3/klines?symbol={mxc_symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000"

            try:
                data = requests.get(url).json()
                df_mxc = pd.DataFrame(data)
                df_mxc = df_mxc.iloc[:,[0,2,3,4]]
                df_mxc[0] = pd.to_datetime(df_mxc[0],unit='ms')
                df_mxc.columns = ['open_time','high','low','close']
                df_mxc[['high','low','close']] = df_mxc[['high','low','close']].astype(float)
                df_mxc['open_time'] = pd.to_datetime(df_mxc['open_time'],unit='ms')
         
                df_mxc.sort_values(by='open_time',inplace=True)
                if '1000' in base_asset:
                    df_mxc['close'] = df_mxc['close']*1000
                    df_mxc['high'] = df_mxc['high']*1000
                    df_mxc['low'] = df_mxc['low']*1000
                elif base_asset == '1MBABYDOGE':
                    df_mxc['close'] = df_mxc['close']*1000000
                    df_mxc['high'] = df_mxc['high']*1000000
                    df_mxc['low'] = df_mxc['low']*1000000
                print('MXC price url: \n',url)
                print(df_mxc.head())
    
            except Exception as e:
                print(e)
                print(url)
        else:
            df_mxc = pd.DataFrame(columns =['open_time','high','low','close'])

      

        # Align exchanges prices 
        startTime = df_binance_futures['open_time'].min()
        endTime = df_binance_futures['open_time'].max()
        print('Binance Futures DataFrame:')
        print(df_binance_futures)
        if interval == '1m':
            freq = '1min'
        else:
            freq = '5min'
        time_df = pd.DataFrame(pd.date_range(startTime,endTime,freq=freq),columns = ['open_time'])

        if len(df_binance) <0:
            df_binance = pd.DataFrame(columns =['open_time','high','low','close'])
        if len(df_okx) >0:
            df_okx_aligned = pd.merge(left=time_df,right=df_okx,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
        else:
            df_okx_aligned = df_okx
        if len(df_bitget) > 0:
            df_bitget_aligned = pd.merge(left=time_df,right=df_bitget,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
        else:
            df_bitget_aligned = df_bitget
        if len(df_kucoin) >0:
            df_kucoin_aligned = pd.merge(left=time_df,right=df_kucoin,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
        else:
            df_kucoin_aligned = df_kucoin
        if len(df_gateio)>0:
            df_gateio_aligned = pd.merge(left=time_df,right=df_gateio,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
        else:
            df_gateio_aligned = df_gateio
        if len(df_bybit)>0:
            df_bybit_aligned = pd.merge(left=time_df,right=df_bybit,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
        else:
            df_bybit_aligned = df_bybit
        if len(df_huobi)>0:
            df_huobi_aligned = pd.merge(left=time_df,right=df_huobi,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
        else:
            df_huobi_aligned = df_huobi
        if len(df_mxc)>0:
            df_mxc_aligned = pd.merge(left=time_df,right=df_mxc,on='open_time',how='left').fillna(method='ffill').fillna(method='bfill')
            # print(df_mxc_aligned)
        else:
            df_mxc_aligned = df_mxc
        # print(df_kucoin_aligned)

        return jsonify({
            'times': df_binance_futures['open_time'].tolist(),
            'closes_binanceSpot': df_binance['close'].tolist(),
            'highs_binanceSpot': df_binance['high'].tolist(),
            'lows_binanceSpot': df_binance['low'].tolist(),
            'closes_binanceIndex': df_binance_index['close'].tolist(),
            'highs_binanceIndex': df_binance_index['high'].tolist(),
            'lows_binanceIndex': df_binance_index['low'].tolist(),
            'closes_binanceFutures': df_binance_futures['close'].tolist(),
            'highs_binanceFutures': df_binance_futures['high'].tolist(),
            'lows_binanceFutures': df_binance_futures['low'].tolist(),
            'closes_binanceMarkPrice': df_binance_markPrice['close'].tolist(),
            'highs_binanceMarkPrice': df_binance_markPrice['high'].tolist(),
            'lows_binanceMarkPrice': df_binance_markPrice['low'].tolist(),
            'closes_bitget': df_bitget_aligned['close'].tolist(),
            'highs_bitget': df_bitget_aligned['high'].tolist(),
            'lows_bitget': df_bitget_aligned['low'].tolist(),
            'closes_kucoin': df_kucoin_aligned['close'].tolist(),
            'highs_kucoin': df_kucoin_aligned['high'].tolist(),
            'lows_kucoin': df_kucoin_aligned['low'].tolist(),
            'closes_okx': df_okx_aligned['close'].tolist(),
            'highs_okx': df_okx_aligned['high'].tolist(),
            'lows_okx': df_okx_aligned['low'].tolist(),
            'closes_gateio': df_gateio_aligned['close'].tolist(),
            'highs_gateio': df_gateio_aligned['high'].tolist(),
            'lows_gateio': df_gateio_aligned['low'].tolist(),
            'closes_bybit': df_bybit_aligned['close'].tolist(),
            'highs_bybit': df_bybit_aligned['high'].tolist(),
            'lows_bybit': df_bybit_aligned['low'].tolist(),
            'closes_huobi': df_huobi_aligned['close'].tolist(),
            'highs_huobi': df_huobi_aligned['high'].tolist(),
            'lows_huobi': df_huobi_aligned['low'].tolist(),
            'closes_mxc': df_mxc_aligned['close'].tolist(),
            'highs_mxc': df_mxc_aligned['high'].tolist(),
            'lows_mxc': df_mxc_aligned['low'].tolist()
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True,port=3000)
