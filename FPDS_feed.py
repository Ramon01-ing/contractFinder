import pandas as pd
import requests
from bs4 import BeautifulSoup


def argsToUrl(args_dict: dict) -> str:
    """Convierte el diccionario de argumentos en un string listo para agregar al url
        feed = "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q" """
    args_dict_copy = dict(args_dict)  # Se copia en variable local para no modificar el dict original
    url_args = '=' + args_dict_copy['=']
    del args_dict_copy['=']
    for k, v in args_dict_copy.items():
        url_args += '%20' + k + ':' + v
    return url_args


def FPDSFeed(feed='https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q', topic='Construction',
             fiscal_year='2021', city='chicago'):
    args = {"=": topic,  # topic debe tener siempre '=' como Key
            "CONTRACT_FISCAL_YEAR": fiscal_year,
            "VENDOR_ADDRESS_CITY": city}

    # "PRINCIPAL_NAICS_CODE": input("PRINCIPAL_NAICS_CODE:")}

    # URL inicial hecha con los parametos parseando de diccionario a url.
    parsed_args = argsToUrl(args)
    # print(parsed_args)
    url = feed + parsed_args
    print('Downloading contracts from FPDS.gov..')

    # Llamamos al URL inicial
    xml_data = requests.get(url).content
    soup = BeautifulSoup(xml_data, "xml")

    # Buscamos el enlace hacia la siguiente pagina del feed
    next_page = soup.find("link", rel="next")
    df_FPDS = pd.DataFrame()

    # Iteramos para obtener las 10 primeras paginas del feed
    for _ in range(10):
        try:
            next_page = soup.find("link", rel="next")
            next_url = next_page['href']  # Enlace hacia la siguiente pagina del feed
        except:
            print('No next page found')
            break
        xml_data = requests.get(next_url).content  # Hacemos la llamada del enlace
        soup = BeautifulSoup(xml_data, "xml")

        for entry in soup.find_all("entry"):
            try:
                OfficeAgency = ''.join(entry.find('ns1:contractingOfficeAgencyID').get('departmentName'))
            except Exception:
                OfficeAgency = ''

            try:
                Title = ''.join(entry.find('title'))
            except Exception:
                Title = ''

            try:
                ID = ''.join(entry.find('ns1:PIID')).strip()
            except Exception:
                ID = ''

            try:
                AgencyID = ''.join(entry.find('ns1:agencyID').get('name')).strip()
            except Exception:
                AgencyID = ''

            try:
                SignedDate = ''.join(entry.find('ns1:signedDate').text)
            except Exception:
                SignedDate = ''

            try:
                CurrentCompletionDate = ''.join(entry.find('ns1:currentCompletionDate').text)
            except Exception:
                CurrentCompletionDate = ''

            try:
                UltimateCompletionDate = ''.join(entry.find('ns1:ultimateCompletionDate').text)
            except Exception:
                UltimateCompletionDate = ''

            try:
                ContractingOfficeID = ''.join(entry.find('ns1:contractingOfficeID').get('name'))
            except Exception:
                ContractingOfficeID = ''

            try:
                ContractActionType = ''.join(entry.find('ns1:contractActionType').get('description'))
            except Exception:
                ContractActionType = ''

            try:
                TypeOfContractPricing = ''.join(entry.find('ns1:typeOfContractPricing').get('description'))
            except Exception:
                TypeOfContractPricing = ''

            try:
                DescriptionOfContractRequirement = ''.join(entry.find('ns1:descriptionOfContractRequirement'))
            except Exception:
                DescriptionOfContractRequirement = ''

            try:
                streetAddress = ''.join(entry.find('ns1:streetAddress'))
            except Exception:
                streetAddress = ''

            try:
                ZipCode = ''.join(entry.find('ns1:vendorAlternateSiteCode'))
            except Exception:
                ZipCode = ''

            try:
                phoneNo = ''.join(entry.find('ns1:phoneNo'))
            except Exception:
                phoneNo = ''

            try:
                faxNo = ''.join(entry.find('ns1:faxNo'))
            except Exception:
                faxNo = ''

            try:
                email = ''.join(entry.find('ns1:createdBy'))
            except Exception:
                email = ''

            try:
                principalNAICS = ''.join(entry.find('ns1:principalNAICSCode'))
            except Exception:
                principalNAICS = ''

            try:
                descriptionNAICS = ''.join(entry.find('ns1:principalNAICSCode').get('description'))
            except Exception:
                descriptionNAICS = ''

            try:
                amount = ''.join(entry.find('ns1:totalBaseAndAllOptionsValue'))
            except Exception:
                amount = ''

            try:
                link = ''.join(entry.find('ns1:websiteURL'))
            except Exception:
                link = ''

            try:
                state = ''.join(entry.find('ns1:state'))
            except Exception:
                state = ''

            try:
                city = ''.join(entry.find('ns1:ZIPCode').get('city'))
            except Exception:
                city = ''

            try:
                # Next sibling of child, here: entry
                entry = entry.find_next_sibling('entry')
            except Exception:
                break

            data = {"Title": Title,
                    "AgencyID": AgencyID,
                    "ID": ID,
                    "SignedDate": SignedDate,
                    "CurrentCompletionDate": CurrentCompletionDate,
                    "UltimateCompletionDate": UltimateCompletionDate,
                    "OfficeAgency": OfficeAgency,
                    "ContractingOfficeID": ContractingOfficeID,
                    "ContractActionType": ContractActionType,
                    "TypeOfContractPricing": TypeOfContractPricing,
                    "DescriptionOfContractRequirement": DescriptionOfContractRequirement,
                    "streetAddress": streetAddress,
                    "ZipCode": ZipCode,
                    "phoneNo": phoneNo,
                    "faxNo": faxNo,
                    "email": email,
                    "principalNAICS": principalNAICS,
                    "descriptionNAICS": descriptionNAICS,
                    "amount$": amount,
                    "link": link,
                    "state": state,
                    "city": city}
            df_FPDS = df_FPDS.append(data, ignore_index=True)

    print(f'Downloaded {len(df_FPDS)} contracts.')
    # print(final_data)
    # fecha = datetime.date.today()
    # archivo = "FPDS"
    # final_data.to_csv(f"{archivo}_{fecha}.csv", index=False)

    return df_FPDS
