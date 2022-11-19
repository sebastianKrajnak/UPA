import pandas as pd
import seaborn as sns
from tqdm import tqdm

df = pd.read_csv("penguins_lter.csv")

# prozkoumejte jednotlivé atributy datové sady, jejich typ a hodnoty, kterých nabývají
print("Concise summary about the data: ")
print(df.info())

print("\n Descriptive statistics: ")
print(df.describe())

# proveďte podrobnou analýzu chybějící hodnot (celkový počet chybějících hodnot,
# počet objektů s více chybějícími hodnotami atd.).
print("\n Number of null values: ")
print(df.isnull().sum())
