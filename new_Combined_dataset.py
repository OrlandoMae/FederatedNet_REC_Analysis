# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 17:23:43 2024

@author: omaer
"""
import pandas as pd

# Carica il file Excel
file_path = '../Producer_Data/Adjusted_Dataset.xlsx'
xls = pd.ExcelFile(file_path)

# Estrai i fogli rilevanti
total_producers = pd.read_excel(xls, 'Total Producers')
weather = pd.read_excel(xls, 'Weather').drop(columns=['SeasonCode', 'Season', 'Month'])
total_consumers = pd.read_excel(xls, 'Total Consumers')
public_building = pd.read_excel(xls, 'PublicBuilding')

# Crea il dataframe per i produttori
producers = total_producers[['datetime']].copy()
producers['total_production'] = total_producers.iloc[:, 1:15].sum(axis=1)

# Aggiungi 'publicconsumption' ai consumatori totali e crea la nuova colonna 'totalconsumption'
total_consumers['publicconsumption'] = public_building['Total Consumption']
total_consumers['totalconsumption'] = total_consumers.iloc[:, 1:].sum(axis=1)

# Crea un nuovo oggetto Excel writer e salva i dataframes in fogli separati
output_path = 'New_Combined_Dataset.xlsx'
with pd.ExcelWriter(output_path) as writer:
    producers.to_excel(writer, sheet_name='producers', index=False)
    weather.to_excel(writer, sheet_name='weather', index=False)
    total_consumers.to_excel(writer, sheet_name='consumers', index=False)

