
AV_STORIC_API = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}&datatype=csv&outputsize=full"
DB_NAME = "financial_data"

QUERY_INSERT_HISTORICAL = "INSERT INTO stock_data (date, open, high, low, close, volume, ticker) VALUES (%(date)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(ticker)s)"