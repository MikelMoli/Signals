import pandas as pd
import yaml
import os
import sys
import psycopg2
import psycopg2.extras

sys.path.insert(0,"/opt/airflow/dags/utils")
# import dags.utils.settings as utils   # Uncomment this in airflow 
# sys.path.insert(0, "/home/mol/Escritorio/Proyectos/Signals/") # Comment this in airflow
import utils.settings as utils  



class ExtractStockHistoricalDataTask():

    def __init__(self, ticker):
        self.ticker = ticker
        with open('/opt/airflow/dags/utils/credentials.yaml') as file:
            credentials = yaml.load(file, Loader=yaml.FullLoader)
            self.api_key = credentials['alpha_vantage_api_key']
            file.close()

    def cross_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        periods = [50, 100, 200]
        for period in periods:
            key = 'ema_' + str(period)
            data[key] = data['close'].ewm(span=period,min_periods=0,adjust=False,ignore_na=False).mean()

        if (data[data.ema_200.isna()].date.max().year < 2005):
            data = data[~data.ema_200.isna()]
        data.reset_index(drop=True, inplace=True)

        data[['shifted_ema_50', 'shifted_ema_100', 'shifted_ema_200']] = data[['ema_50', 'ema_100', 'ema_200']].shift(1)
        data[['50_cross_100', '50_cross_200', '100_cross_200']] = '-'
        data.loc[(data['ema_50'] > data['ema_100']) & (data['shifted_ema_50'] < data['shifted_ema_100']), '50_cross_100'] = 'BUY'
        data.loc[(data['ema_50'] > data['ema_200']) & (data['shifted_ema_50'] < data['shifted_ema_200']), '50_cross_200'] = 'BUY'
        data.loc[(data['ema_100'] > data['ema_200']) & (data['shifted_ema_100'] < data['shifted_ema_200']), '100_cross_200'] = 'BUY'

        data.loc[(data['ema_50'] < data['ema_100']) & (data['shifted_ema_50'] > data['shifted_ema_100']), '50_cross_100'] = 'SELL'
        data.loc[(data['ema_50'] < data['ema_200']) & (data['shifted_ema_50'] > data['shifted_ema_200']), '50_cross_200'] = 'SELL'
        data.loc[(data['ema_100'] < data['ema_200']) & (data['shifted_ema_100'] > data['shifted_ema_200']), '100_cross_200'] = 'SELL'
        
        return data

    def _format_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data.rename(columns={'timestamp': 'date'}, inplace=True)
        data['date'] = pd.to_datetime(data['date'])
        #data['date'] = data['date'].dt.strftime('%Y-%m-%d').astype('str')
        data = data.sort_values(by='date', ascending=True)
        return data

    def run(self):
        data = pd.read_csv(utils.AV_STORIC_API.format(self.ticker, self.api_key))
        data['ticker'] = self.ticker
        data = self._format_data(data)
        data.to_dict(orient='records')
        try:
            conn = psycopg2.connect(
                host="signals_postgres_1", # name of container
                port="5432",
                database='financial_data',
                user='airflow',
                password='airflow'
            )

            with conn.cursor() as cur:
                query = utils.QUERY_INSERT_HISTORICAL
                psycopg2.extras.execute_batch(cur=cur, sql=query, 
                                              argslist=data.to_dict(orient='records'))
                conn.commit()
        finally:
            if conn is not None:
                conn.close()

        # data = self.cross_signals(data)
        # try:
        #     os.mkdir('/opt/airflow/data')
        # except FileExistsError:
        #     print('Folder was already created')
        # data.to_csv('/opt/airflow/data/prueba.csv', index=False)

def extract():
    task = ExtractStockHistoricalDataTask('IBM')
    task.run()

#if __name__=='__main__':
# print('STARTING')
# print("HELLO WORLD")
# ticker_list = ['IBM']
# for ticker in ticker_list:
#     task = ExtractStockDataTask(ticker)
#     task.run() 