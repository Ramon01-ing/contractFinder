import datetime
from os import path

import numpy as np
import pandas as pd


def filterContractsByNaics(contracts_csv_path, naics_code_start_digits='23'):
    print('filterContractsByNaics')
    date = datetime.date.today()
    cvs_name = "BetaSamFiltered"
    #if not path.exists(f"{cvs_name}_{date}.csv"):
    if not path.exists(f"csvs/{cvs_name}_{date}.csv"):
        print(f'Filtering BetaSamCvs by NAICS code {naics_code_start_digits}..')
        df = pd.read_csv(contracts_csv_path, low_memory=False)
        df = df.applymap(str)
        criteria = df['NaicsCode'].str.startswith(naics_code_start_digits)
        df_BetaSamFiltered = df[criteria]
        #df_BetaSamFiltered.to_csv(f"{cvs_name}_{date}.csv", index=False)
        df_BetaSamFiltered.to_csv(f"csvs/{cvs_name}_{date}.csv", index=False)
        print(f'Filtered done.')
    else:
        print(f'BetaSamCvs was already filtered by NAICS code today.')
        # df_BetaSamFiltered = pd.read_csv(f"{cvs_name}_{date}.csv")
        df_BetaSamFiltered = pd.read_csv(f"csvs/{cvs_name}_{date}.csv")

    return df_BetaSamFiltered


def order_columns_FullBetaSam(df_BetaSamFiltered: pd.DataFrame):
    # fecha = datetime.date.today()
    # archivo = 'BetaSamFiltered'
    # df1 = pd.read_csv(f"{archivo}_{fecha}.csv", low_memory=False)
    df = df_BetaSamFiltered
    df.drop(['PrimaryContactFullname', 'SecondaryContactFax', 'SecondaryContactPhone', 'SecondaryContactEmail',
             'SecondaryContactFullname', 'Sol#', 'CGAC', 'FPDS Code', 'AAC Code', 'ArchiveType', 'SetASideCode',
             'SetASide', 'ClassificationCode', 'PopCity', 'PopState', 'PopZip', 'PopCountry', 'AwardNumber',
             'AwardDate', 'Awardee', 'PrimaryContactTitle', 'SecondaryContactTitle', 'OrganizationType', 'CountryCode',
             'AdditionalInfoLink'], axis=1, inplace=True)

    df.columns = ['ID', 'Title', 'AgencyID', 'OfficeAgency',
                  'ContractingOfficeID', 'SignedDate', 'ContractActionType',
                  'TypeOfContractPricing', 'UltimateCompletionDate', 'CurrentCompletionDate',
                  'principalNAICS', 'streetAddress', 'Active', 'amount$',
                  'email', 'phoneNo', 'faxNo', 'state', 'city', 'ZipCode',
                  'link', 'DescriptionOfContractRequirement']

    condiciones = [
        (df['principalNAICS'] == 23), (df['principalNAICS'] == 2361), (df['principalNAICS'] == 236115),
        (df['principalNAICS'] == 236116), (df['principalNAICS'] == 236117), (df['principalNAICS'] == 236118),
        (df['principalNAICS'] == 2362), (df['principalNAICS'] == 236210), (df['principalNAICS'] == 236220),
        (df['principalNAICS'] == 2371), (df['principalNAICS'] == 237110), (df['principalNAICS'] == 237120),
        (df['principalNAICS'] == 237130),
        (df['principalNAICS'] == 2372), (df['principalNAICS'] == 237210),
        (df['principalNAICS'] == 2373), (df['principalNAICS'] == 237310),
        (df['principalNAICS'] == 2379), (df['principalNAICS'] == 237990),
        (df['principalNAICS'] == 2381), (df['principalNAICS'] == 238110), (df['principalNAICS'] == 238120),
        (df['principalNAICS'] == 238130), (df['principalNAICS'] == 238140), (df['principalNAICS'] == 238150),
        (df['principalNAICS'] == 238160), (df['principalNAICS'] == 238170), (df['principalNAICS'] == 238190),
        (df['principalNAICS'] == 2382), (df['principalNAICS'] == 238210), (df['principalNAICS'] == 238220),
        (df['principalNAICS'] == 238290),
        (df['principalNAICS'] == 2383), (df['principalNAICS'] == 238310), (df['principalNAICS'] == 238320),
        (df['principalNAICS'] == 238330), (df['principalNAICS'] == 238340), (df['principalNAICS'] == 238350),
        (df['principalNAICS'] == 238390),
        (df['principalNAICS'] == 2389), (df['principalNAICS'] == 238910), (df['principalNAICS'] == 238990)
    ]

    opciones = ['Construction', 'Residential Building Construction', 'New Single-Family Housing Construction',
                'New Multifamily Housing Construction', 'New Housing For-Sale Builders', 'Residential Remodelers',
                'Nonresidential Building Construction', 'Industrial Building Construction',
                'Commercial and Institutional Building Construction',
                'Utility System Construction', 'Water and Sewer Line and Related Structures Construction',
                'Oil and Gas Pipeline and Related Structures Construction',
                'Power and Communication Line and Related Structures Construction',
                'Land Subdivision', 'Land Subdivision',
                'Highway, Street, and Bridge Construction', 'Highway, Street, and Bridge Construction',
                'Other Heavy and Civil Engineering Construction', '	Other Heavy and Civil Engineering Construction',
                'Foundation, Structure, and Building Exterior Contractors',
                'Poured Concrete Foundation and Structure Contractors',
                'Structural Steel and Precast Concrete Contractors', 'Framing Contractors', 'Masonry Contractors',
                'Glass and Glazing Contractors', 'Roofing Contractors', 'Siding Contractors',
                'Other Foundation, Structure, and Building Exterior Contractors',
                'Building Equipment Contractors', 'Electrical Contractors and Other Wiring Installation Contractors',
                'Plumbing, Heating, and Air-Conditioning Contractors', 'Other Building Equipment Contractors',
                'Building Finishing Contractors', 'Drywall and Insulation Contractors',
                'Painting and Wall Covering Contractors', 'Flooring Contractors', '	Tile and Terrazzo Contractors',
                'Finish Carpentry Contractors', 'Other Building Finishing Contractors',
                'Other Specialty Trade Contractors', 'Site Preparation Contractors',
                'All Other Specialty Trade Contractors']

    df['descriptionNAICS'] = np.select(condiciones, opciones)

    df_BetaSamOrdered = df[['AgencyID', 'ContractActionType', 'ContractingOfficeID',
                            'CurrentCompletionDate', 'DescriptionOfContractRequirement',
                            'ID', 'OfficeAgency', 'SignedDate', 'Title', 'TypeOfContractPricing',
                            'UltimateCompletionDate', 'ZipCode', 'amount$', 'city', 'descriptionNAICS',
                            'email', 'faxNo', 'link', 'phoneNo', 'principalNAICS', 'state',
                            'streetAddress']]

    # df1.to_csv(f"{archivo}_{fecha}.csv", index=False)
    return df_BetaSamOrdered


def join_FPDS_and_orderBetaSam(df_BetaSamOrdered: pd.DataFrame, df_FPDS: pd.DataFrame) -> pd.DataFrame:
    df_BetaSamOrdered = df_BetaSamOrdered
    df_FPDS = df_FPDS
    # extension = 'csv'
    # fecha = datetime.date.today()
    # all_filenames = [i for i in glob.glob('*{}.{}'.format(fecha, extension))]
    # print(all_filenames)

    # combine all files in the list
    # df_combined = pd.concat([pd.read_csv(f) for f in all_filenames])
    df_joined_FPDS_BetaSam = pd.concat([df_FPDS, df_BetaSamOrdered])
    # export to csv
    # archivo = 'combined'
    # fecha = datetime.date.today()
    # df_combined.to_csv(f"{archivo}_{fecha}.csv", index=False, encoding='utf-8-sig')

    return df_joined_FPDS_BetaSam
