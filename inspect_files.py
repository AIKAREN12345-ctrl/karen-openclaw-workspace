import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference, PieChart
from openpyxl.utils.dataframe import dataframe_to_rows

# Load all three files
print("Loading file 191 (Chocolate Sales Data)...")
df1 = pd.read_excel('C:/Users/Karen/.openclaw/media/inbound/file_191---1d6a3fcf-e32b-413e-8746-b239ed12319a.xlsx')
print(f"File 191 shape: {df1.shape}")
print(f"File 191 columns: {df1.columns.tolist()}")
print("\nFirst 10 rows:")
print(df1.head(10))

print("\n" + "="*60)
print("Loading file 192 (Classmate's workings)...")
df2 = pd.read_excel('C:/Users/Karen/.openclaw/media/inbound/file_192---d557f616-4976-476b-ae78-fb9a252cc8fd.xlsx')
print(f"File 192 shape: {df2.shape}")
print(f"File 192 columns: {df2.columns.tolist()}")
print("\nFirst 10 rows:")
print(df2.head(10))

print("\n" + "="*60)
print("Loading file 193 (if needed)...")
df3 = pd.read_excel('C:/Users/Karen/.openclaw/media/inbound/file_193---c55d0a87-d312-43c7-8d73-afa4b213691c.xlsx')
print(f"File 193 shape: {df3.shape}")
print(f"File 193 columns: {df3.columns.tolist()}")
print("\nFirst 10 rows:")
print(df3.head(10))
