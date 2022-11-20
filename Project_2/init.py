import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("penguins_lter.csv")

# prozkoumejte jednotlivé atributy datové sady, jejich typ a hodnoty, kterých nabývají
print("Concise summary about the data: \n")
print(df.info())

# Amend for pandas type inferring and cast object type columns to string
to_string = list(df.select_dtypes(include="object").columns)
df[to_string] = df[to_string].astype("string")

print("\nDescriptive statistics:\n", df.describe())

# proveďte podrobnou analýzu chybějící hodnot (celkový počet chybějících hodnot,
# počet objektů s více chybějícími hodnotami atd.).

print("\nNumber of null values:\n", df.isnull().sum())

# We can fix the missing value in Delta 15 N and Delta 13 C however seeing as we already know they won't be neccessary for the classification
# dataset, we will just drop them off completely. Comments won't be needed for classification at all
only_one_unique = df.nunique()[df.nunique() == 1].index
print("\nNumber of unique entries for each attribute:\n", df.nunique())
print("\nAttributes with only one unique value: ", only_one_unique.tolist())

drop_atrs = only_one_unique.tolist() + [
    "Delta 15 N (o/oo)",
    "Delta 13 C (o/oo)",
    "Comments",
]
df.drop(drop_atrs, axis=1, inplace=True)

fig, axes = plt.subplots(2, 2)

# Before filling null values, we need to check numerical attributes for outliers using boxplot
sns.boxplot(ax=axes[0, 0], y="Flipper Length (mm)", data=df)
axes[0, 0].set_title("Flipper Length (mm)")
sns.boxplot(ax=axes[0, 1], y="Culmen Length (mm)", data=df)
axes[0, 1].set_title("Culmen Length (mm)")
sns.boxplot(ax=axes[1, 0], y="Culmen Depth (mm)", data=df)
axes[1, 0].set_title("Culmen Depth (mm)")
sns.boxplot(ax=axes[1, 1], y="Body Mass (g)", data=df)
axes[1, 1].set_title("Body Mass (g)")

plt.show()

# print(df.loc[3])
# Fill up the missing values with mean for numerical attributes and mode for categorical attributes
for col in df.columns:
    if df[col].isnull().any() == True:
        if df[col].dtype == "float64":
            df[col] = df[col].fillna(df[col].mean())
        if df[col].dtype == "string":
            df[col] = df[col].fillna(df[col].mode()[0])

# print(df.loc[3])
