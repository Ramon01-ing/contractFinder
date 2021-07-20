"""Descarga y guarda como ContractsFullBetaSam_date.csv el ultimo csv de las oportunidades de contrato de la pagina de
BetaSam.gov, usando pandas y el link directo de descarga."""

import datetime
import time
from os import path
import pandas as pd


def downloadBetaSamCsv():
    print('downloadBetaSamCsv')
    # Just download BetaSamCsv once per day.
    date = datetime.date.today()
    csv_name = "ContractsFullBetaSam"
    #if path.exists(f'{csv_name}_{date}.csv'):
    if path.exists(f'csvs/{csv_name}_{date}.csv'):
        print('BetaSamCsv up to date.')
        return None
    start = time.perf_counter()
    print('Downloading all contract opportunities CSV from BetaSam.gov..')
    # For Windows use pd.read_csv with encoding='cp1252'
    df = pd.read_csv(
        'https://sam.gov/api/prod/fileextractservices/v1/api/download/Contract%20Opportunities/datagov/ContractOpportunitiesFullCSV.csv?privacy=Public',
        encoding='cp1252')
    # For Linux/Mac use pd.read_csv with encoding='utf-8'
    # df = pd.read_csv(
    #    'https://sam.gov/api/prod/fileextractservices/v1/api/download/Contract%20Opportunities/datagov/ContractOpportunitiesFullCSV.csv?privacy=Public',
    #    encoding='cp1252')

    df.to_csv(f'csvs/{csv_name}_{date}.csv', index=False)
    print('Saved')

    finish = time.perf_counter()
    print('Finished in {} seconds'.format(round(finish - start, 2)))
