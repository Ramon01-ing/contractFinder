import datetime
import time

from FPDS_feed import FPDSFeed
from downloadBetaSamCsvPandas import downloadBetaSamCsv
from joinFPDS_BetaSam import filterContractsByNaics, order_columns_FullBetaSam, join_FPDS_and_orderBetaSam
from keywords import prepare_df_for_search, get_keywords, search_keywords, createMap


# search_dict = {
#     'state': request.form.get('state'),
#     'city': request.form.get('city'),
#     'business': request.form.get('business'),
#     'keywords1': request.form.get('keywords1'),
#     'keywords2': request.form.get('keywords2'),
#     'keywords3': request.form.get('keywords3')
# }
def search_pipeline(search_dict: dict) -> ('map_html', 'contracts_table_html'):
    date = datetime.date.today()
    downloadBetaSamCsv()
    df_BetaSamFiltered = filterContractsByNaics(contracts_csv_path=f'csvs/ContractsFullBetaSam_{date}.csv')
    df_BetaSamOrdered = order_columns_FullBetaSam(df_BetaSamFiltered)
    df_FPDS = FPDSFeed(topic=search_dict['business'], fiscal_year='2021', city=search_dict['city'])
    df_joined_FPDS_BetaSam = join_FPDS_and_orderBetaSam(df_BetaSamOrdered, df_FPDS)
    df_dropNan = prepare_df_for_search(df_joined_FPDS_BetaSam)
    df_keywords = get_keywords(df_dropNan)
    df_contracts_found = search_keywords(df_keywords, list(search_dict.values()), max_contracts=100)
    # with open('map.html', 'w') as map_file:
    #     map_file.write(createMap(df_contracts_found))
    return createMap(df_contracts_found), df_contracts_found.to_html()

# start = time.perf_counter()
# keywords = ['Kansas', 'hospital']
# print(search_pipeline(keywords)[1])
# finish = time.perf_counter()
# print('Finished in {} seconds'.format(round(finish - start, 2)))
