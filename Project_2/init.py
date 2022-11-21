import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("penguins_lter.csv")
# Amend for pandas type inferring and cast object type columns to string
to_string = list(df.select_dtypes(include="object").columns)
df[to_string] = df[to_string].astype("string")

# 2.1 PROZKOUMEJTE JEDNOTLIVÉ ATRIBUTY DATOVÉ SADY, JEJICH TYP A HODNOTY, KTERÝCH NABÝVAJÍ ----------------------------------------------------
print("Concise summary about the data: \n")
print(df.info())

print("\nDescriptive statistics:\n", df.describe())

# 2.2 PROZKOUMEJTE ROZLOŽENÍ HODNOT JEDNOTLIVÝCH ATRIBUTŮ POMOCÍ VHODNÝCH GRAFŮ, ZAMĚŘTE SE I NA TO,
# JAK HODNOTA JEDNOHO ČI DVOU ATRIBUTŮ OVLIVNÍ ROZLOŽENÍ HODNOT JINÉHO ATRIBUTU -----------------------------------------------------------

# Total number of Sexes and number of Sexes for each Species
fig, axes = plt.subplots(1, 2)
sns.histplot(data=df, x="Sex", ax=axes[0])
sns.countplot(hue="Species", data=df, x="Sex", ax=axes[1])
plt.show()

# Distributions of penguins on the Islands
sns.countplot(x="Island", data=df)
plt.show()

# Relationship between Flipper Length and Body Mass for Sexes and Species
sns.scatterplot(
    x="Flipper Length (mm)", y="Body Mass (g)", data=df, style="Sex", hue="Species"
)
plt.show()

# Relationship between Culmen Length and Depth
sns.scatterplot(x="Culmen Length (mm)", y="Culmen Depth (mm)", data=df, hue="Sex")
plt.show()

# Relationship of Body Mass and Sex for each Species
sns.boxplot(
    x="Sex",
    y="Body Mass (g)",
    hue="Species",
    data=df,
)
plt.show()

# 2.3 ZJISTĚTE, ZDA ZVOLENÁ DATOVÁ SADA OBSAHUJE NĚJAKÉ ODLEHLÉ HODNOTY. ----------------------------------------------------------------------
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

# 2.4 PROVEĎTE PODROBNOU ANALÝZU CHYBĚJÍCÍ HODNOT (CELKOVÝ POČET CHYBĚJÍCÍCH HODNOT,
# POČET OBJEKTŮ S VÍCE CHYBĚJÍCÍMI HODNOTAMI ATD.). ---------------------------------------------------------------------------------------

print("\nNumber of null values:\n", df.isnull().sum())

# We can fix the missing value in Delta 15 N and Delta 13 C however seeing as we already know they won't be neccessary for the classification
# dataset, we will just drop them off completely. Comments won't be needed for classification at all
only_one_unique = df.nunique()[df.nunique() == 1].index
print("\nNumber of unique entries for each attribute:\n", df.nunique())
print("\nAttributes with only one unique value: ", only_one_unique.tolist())


# 2.5 PROVEĎTE KORELAČNÍ ANALÝZU NUMERICKÝCH ATRIBUTŮ -----------------------------------------------------------------------------------------
# Pairplot (matica bodovycch grafov) for numerical attributes
sns.pairplot(df)

# Pairplot (matica bodovycch grafov) for categorical attributes
sns.pairplot(df, hue="Sex")
sns.pairplot(df, hue="Species")

plt.show()

# Heatmap (korelacna matica)
sns.heatmap(df.corr(), annot=True)
plt.show()

# 3.1 ODSTRAŇTE Z DATOVÉ SADY ATRIBUTY, KTERÉ JSOU PRO DANOU DOLOVACÍ ÚLOHU IRELEVANTNÍ. ------------------------------------------------------
drop_atrs = only_one_unique.tolist() + [
    "Delta 15 N (o/oo)",
    "Delta 13 C (o/oo)",
    "Comments",
    "Sample Number",
    "studyName",
    "Individual ID",
]
df.drop(drop_atrs, axis=1, inplace=True)

# 3.2 VYPOŘÁDEJTE SE S CHYBĚJÍCÍMI HODNOTAMI. PRO ODSTRANĚNÍ TĚCHTO HODNOT VYUŽIJTE ALESPOŇ DVĚ RŮZNÉ
# METODY PRO ODSTRANĚNÍ CHYBĚJÍCÍCH HODNOT. ------------------------------------------------------------------------------------------------
# 3.3 VYPOŘÁDEJTE SE S ODLEHLÝMI HODNOTAMI, JSOU-LI V DATOVÉ SADĚ PŘÍTOMNY.
#   nope there are none


# No. of unique value for Sex is 3 which is quite unusual for sex, upon displaying the unique values we see that it has corrupt data
# as . is not a Sex category, we shall replace . with MALE
print(df["Sex"].unique())
print(df.loc[df["Sex"] == "."].index.item())

df["Sex"] = df["Sex"].replace(".", "MALE")

# print("\nCorrected corrupt entry:\n", df.loc[336])

# The first method we used to correct the missing values is to fill them up with mean for numerical attributes and
# mode for categorical attributes, the second method was already done when we dropped some attributes such as Comments which had
# 316 missing values and it would be pointless to try and fill them up

# print("Before correction", df.loc[3])
for col in df.columns:
    if df[col].isnull().any() == True:
        if df[col].dtype == "float64":
            df[col] = df[col].fillna(df[col].mean())
        if df[col].dtype == "string":
            df[col] = df[col].fillna(df[col].mode()[0])

# print("After correction", df.loc[3])

# 3.4 PRO JEDNU VARIANTU DATOVÉ SADY PROVEĎTE DISKRETIZACI NUMERICKÝCH ATRIBUTŮ TAK, ABY VÝSLEDNÁ DATOVÁ SADA BYLA
# VHODNÁ PRO ALGORITMY, KTERÉ VYŽADUJÍ NA VSTUPU KATEGORICKÉ ATRIBUTY.  -------------------------------------------------------------------

# 3.5 PRO DRUHOU VARIANTU DATOVÉ SADY PROVEĎTE VHODNOU TRANSFORMACI KATEGORICKÝCH ATRIBUTŮ NA NUMERICKÉ ATRIBUTY.
# DÁLE PAK PROVEĎTE NORMALIZACI NUMERICKÝCH ATRIBUTŮ, KTERÉ MÁ SMYSL NORMALIZOVAT.
# VÝSLEDNÁ DATOVÁ SADA BY MĚLA BÝT VHODNÁ PRO METODY VYŽADUJÍCÍ NUMERICKÉ VSTUPY.   -------------------------------------------------------
