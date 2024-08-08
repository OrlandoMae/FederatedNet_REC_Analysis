# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 16:27:42 2024

@author: omaer
secondo te si puo migliorare in qualche modo questa pre elaborazione dei dati 
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


# Caricare il file Excel
file_path = 'New_Combined_Dataset.xlsx'
xls = pd.ExcelFile(file_path)

# Caricare i dati dai fogli di lavoro
producers_df = pd.read_excel(xls, 'producers')
weather_df = pd.read_excel(xls, 'weather')
consumers_df = pd.read_excel(xls, 'consumers')

# Unire i dataframes sul campo 'datetime'
merged_df = producers_df.merge(weather_df, on='datetime').merge(consumers_df, on='datetime')

# Gestione dei valori mancanti
# Riempire i valori mancanti utilizzando la media per ciascuna colonna
merged_df.fillna(merged_df.mean(), inplace=True)

# Conversione della colonna datetime in formato datetime di pandas
merged_df['datetime'] = pd.to_datetime(merged_df['datetime'])

# Creazione di nuove caratteristiche basate sul tempo
merged_df['hour'] = merged_df['datetime'].dt.hour
merged_df['dayofweek'] = merged_df['datetime'].dt.dayofweek
merged_df['month'] = merged_df['datetime'].dt.month
merged_df['weekofyear'] = merged_df['datetime'].dt.isocalendar().week
merged_df['is_weekend'] = merged_df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)

# Creazione della caratteristica 'season'
def get_season(month):
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:
        return 'fall'

merged_df['season'] = merged_df['month'].apply(get_season)

# Mantieni a zero la produzione di notte (ad esempio per i pannelli solari)
merged_df.loc[(merged_df['hour'] >= 18) | (merged_df['hour'] <= 5), 'total_production'] = 0

# Convertire tutti i nomi delle colonne in stringhe
merged_df.columns = merged_df.columns.astype(str)

# Normalizzazione dei dati
scaler = MinMaxScaler()
columns_to_scale = merged_df.columns.difference(['datetime', 'season', 'month', 'hour', 'dayofweek', 'weekofyear', 'is_weekend'])
merged_df[columns_to_scale] = scaler.fit_transform(merged_df[columns_to_scale])

# Conversione delle caratteristiche categoriche in dummy/one-hot encoding
merged_df = pd.get_dummies(merged_df, columns=['season', 'month', 'hour', 'dayofweek', 'weekofyear'])

# Rimozione della colonna datetime originale
merged_df.drop('datetime', axis=1, inplace=True)

# Divisione dei dati in set di addestramento e di test (50% ciascuno)
train_df, test_df = train_test_split(merged_df, test_size=0.5, random_state=42, shuffle=True)

# Salva i dataframe pre-elaborati su file CSV
train_df.to_csv('training_data.csv', index=False)
test_df.to_csv('testing_data.csv', index=False)

# Visualizzazione dei primi 5 record dei set di addestramento e di test
print("Training Data:")
print(train_df.head())

print("\nTesting Data:")
print(test_df.head())

