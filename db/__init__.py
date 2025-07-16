import pandas as pd
df = pd.read_csv("data/productos.csv", nrows=1)
print(df.columns.tolist())
