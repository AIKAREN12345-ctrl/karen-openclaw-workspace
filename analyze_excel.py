import pandas as pd

df = pd.read_excel('C:/Users/Karen/.openclaw/media/inbound/file_191---1d6a3fcf-e32b-413e-8746-b239ed12319a.xlsx')

# Clean up - remove the header row that's in the data
df = df[df['Sales Person'] != 'Jehu Rudeforth'].reset_index(drop=True)
df = df[df['Sales Person'] != 'Sales Person'].reset_index(drop=True)

# Keep only relevant columns
df = df[['Sales Person', 'Country', 'Product', 'Date', 'Amount', 'Boxes Shipped']]

print("Cleaned Data:")
print(df.head(20))
print("\nShape:", df.shape)
print("\nUnique Countries:", df['Country'].unique())
print("\nUnique Products:", df['Product'].unique())
print("\nDate Range:", df['Date'].min(), "to", df['Date'].max())
print("\nTotal Sales:", df['Amount'].sum())
print("\nTotal Boxes:", df['Boxes Shipped'].sum())
