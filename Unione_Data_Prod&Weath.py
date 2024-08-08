# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 13:04:27 2024

@author: omaer
"""
import pandas as pd


# Percorsi ai file direttamente nella directory dei file caricati
dataset_path = '../../Dataset.xlsx'
weather_data_gen_path = '../Weather_Data/Weather_Data_Gen.xlsx'
completed_processed_path = 'Completed_Processed.xlsx'

# Leggi il foglio "Weather" da Weather_Data_Gen.xlsx
weather_data_gen = pd.read_excel(weather_data_gen_path, sheet_name='Weather')
total_producers_data = pd.read_excel(completed_processed_path, sheet_name='Total Producers')

# Carica il file Dataset.xlsx e sostituisci il foglio "Weather"
with pd.ExcelWriter(dataset_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    weather_data_gen.to_excel(writer, sheet_name='Weather', index=False)
    total_producers_data.to_excel(writer, sheet_name='Total Producers', index=False)
