import pandas as pd

df = pd.read_csv("economic.csv")
df = df.drop_duplicates()
df.to_csv("economic.csv", index=False)
