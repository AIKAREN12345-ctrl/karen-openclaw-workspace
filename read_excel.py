import pandas as pd

df = pd.read_excel('C:/Users/Karen/.openclaw/media/inbound/file_191---1d6a3fcf-e32b-413e-8746-b239ed12319a.xlsx')
print("First 20 rows:")
print(df.head(20))
print("\nColumns:", df.columns.tolist())
print("\nShape:", df.shape)
print("\nData types:")
print(df.dtypes)
