import re
from collections import Counter
import branca
import folium
import nltk
import numpy as np
import pandas as pd
import pgeocode
from folium import plugins
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


# TODO: Drop 'duplicates' (same contract but slightly dif record)
def prepare_df_for_search(df_joined_FPDS_BetaSam: pd.DataFrame) -> pd.DataFrame:
    print('prepare_df_for_search')

    df = df_joined_FPDS_BetaSam
    # df['ZipCode'] = df['ZipCode'].apply(str)
    df['ZipCode'] = df['ZipCode'].apply(str).apply(lambda x: x[:5])

    # Added column "text" to df:
    # text: All the text of the selected columns from the contracts
    df['text'] = df['AgencyID'].astype(str) + '' + df['ContractingOfficeID'].astype(str) + '' + df[
        'DescriptionOfContractRequirement'].astype(str) + '' + df['OfficeAgency'].astype(str) + '' + df['Title'].astype(
        str) + '' + df['city'] + '' + df['descriptionNAICS'].astype(str) + '' + df['state'].astype(str) + '' + df[
                     'ZipCode'].astype(str) + '' + df['streetAddress'].astype(str)
    df['text'].apply(str)

    # -Remove punctuation
    df.text = df.text.apply(lambda x: re.sub('[^a-zA-Z-[0-9]]', ' ', str(x)))

    # Checks how the word count of the column "text" is distributed
    # We noticed there were many rows with just 1 word, so we filtered by word count
    # print(pd.DataFrame([len(text.split()) for text in df.text]).describe())

    # TODO: Decide which is better high-pass filter or low-pass and high-pass filters
    # Getting rid of rows with less than 5 words or more than 700 words
    # df_drop_nan = df.loc[[((len(text.split()) > 5) & (len(text.split()) < 700)) for text in df.text]]
    df_drop_nan = df.loc[[(len(text.split()) > 5) for text in df.text], :]
    # df_drop_nan = df.loc[(df['text'].str.len() > 10) & (df['text'].str.len() < 2700)]
    # print(pd.DataFrame([len(text.split()) for text in df_drop_nan.text]).describe())

    # Text preprocessing
    # -Lowercase
    # No need to lowercase bcs TfidfVectorizer() automatically converts to lowercase

    # df.text = df.text.apply(str.lower)

    return df_drop_nan.copy(deep=True)  # Deep copy to avoid future Warning (trying to assign value to slice)


def get_keywords(df_dropNan: pd.DataFrame, k=25) -> pd.DataFrame:
    print('get_keywords')
    """
    Adds a column to the df:
     -keywords: Most important words of each contract (using TF-IDF)
    """
    nltk.download('stopwords')

    # Vectorize, removing stopwords and convert to lowercase
    tfidf = TfidfVectorizer(max_features=5000,
                            stop_words=nltk.corpus.stopwords.words('english'),
                            lowercase=True)
    X = tfidf.fit_transform(df_dropNan.text)

    # Making sure all features have 0 mean and unit standard deviation
    scaler = StandardScaler()
    X = scaler.fit_transform(X.todense())

    feature_names = tfidf.get_feature_names()
    keywords = []
    for i in range(X.shape[0]):
        text_vector = X[i]
        idxs = np.array(text_vector.argsort()[-k:][::-1]).T  # Getting the index of vip words (bigger tfidf)
        s = ''
        for j in range(k):
            # sometimes 25 keywords are too much, so I make sure I don't get useless words
            if text_vector[idxs[j]] != 0:
                s = s + feature_names[idxs[j]] + ','
        keywords.append(s)
    df_dropNan['keywords'] = keywords
    df_keywords = df_dropNan
    return df_keywords


def search_keywords(df_keywords, user_keywords: [], max_contracts=100):
    print('search_keywords')
    idxs = []
    user_keywords = list(map(lambda x: x.lower(), user_keywords))
    for user_keyword in user_keywords:
        if not user_keyword:
            continue
        print(user_keyword)
        bools = df_keywords.keywords.apply(lambda x: user_keyword in x)  # Bool array: Does this text have this keyword?
        idxs.extend(list(df_keywords.keywords.loc[bools].index))  # Keeps track of the texts that have keywords
        # df_contracts_found = pd.DataFrame(
        #     columns=['AgencyID', 'DescriptionOfContractRequirement', 'city', 'link', 'phoneNo', 'streetAddress',
        #              'ZipCode'])
        # user_keywords_text = []
        # for idx, count in zip(counter.keys(), counter.values()):
        #     aux = df_keywords.loc[idx][
        #         ['AgencyID', 'DescriptionOfContractRequirement', 'city', 'link', 'phoneNo', 'streetAddress',
        #          'ZipCode']]
        #
        #     s = [user_keyword for user_keyword in user_keywords if user_keyword in df_keywords.loc[idx]['keywords']]
        #     s = ','.join(s)
        #     user_keywords_text.append(s)
        #
        #     df_contracts_found = df_contracts_found.append(aux)

        # df_contracts_found.reset_index(inplace=True)
        # del df_contracts_found['index']
        # df_contracts_found.columns = ['Agency', 'Description', 'City', 'Link', 'Phone Number', 'Street Address',
        #                               'Zip Code']
        # df_contracts_found['Keywords'] = user_keywords_text

    counter = Counter(idxs)
    # counter = {k: v for k, v in sorted(dict(Counter(idxs)).items(), key=lambda item: item[1], reverse=True)}
    df_contracts_found = df_keywords.loc[[value[0] for value in counter.most_common(max_contracts)]]
    df_contracts_found = df_contracts_found.loc[:,
                         ['AgencyID', 'DescriptionOfContractRequirement', 'city', 'link', 'phoneNo', 'streetAddress',
                          'ZipCode']]
    df_contracts_found.columns = ['Agency', 'Description', 'City', 'Link', 'Phone Number', 'Street Address', 'Zip Code']
    df_contracts_found.reset_index(inplace=True)
    return df_contracts_found


def createMap(df_contracts_found):
    print('createMap')
    nomi = pgeocode.Nominatim('US')
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4, control_scale=True)
    tooltip = "Click me!"
    marker_cluster = plugins.MarkerCluster().add_to(m)
    print('df_contracts_found:', len(df_contracts_found))
    for i in range(len(df_contracts_found)):
        Agency_Name = df_contracts_found.loc[i, 'Agency']
        Desc = df_contracts_found.loc[i, 'Description']
        City = df_contracts_found.loc[i, 'City']
        Link = df_contracts_found.loc[i, 'Link']
        Phone = df_contracts_found.loc[i, 'Phone Number']
        Address = df_contracts_found.loc[i, 'Street Address']
        ZIPCode = df_contracts_found.loc[i, 'Zip Code']

        header_colour = "#2A799C"
        data_colour = "#C5DCE7"

        html = """
        <table style="width: 100%">
        <caption align:left>Contract Information</caption>
        <tbody>
        <tr>
        <td style="background-color: """ + header_colour + """ ;"><span style="color: #ffffff;">Agency Name</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """ ;">{}</td>""".format(Agency_Name) + """
        </tr>
        <tr>
        <td style="background-color: """ + header_colour + """ ;"><span style="color: #ffffff;">Description</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """ ;">{}</td>""".format(Desc) + """
        </tr>
        <tr>
        <td style="background-color: """ + header_colour + """; "><span style="color: #ffffff;">City</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """ ;">{}</td>""".format(City) + """
        </tr>
        <tr>
        <td style="background-color: """ + header_colour + """;"><span style="color: #ffffff;">BetaSam.gov</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """ ;"><a href={} target="_blank">Complete Contract Info</a></td>""".format(
            Link) + """
        </tr>
        <tr>
        <td style="background-color: """ + header_colour + """; "><span style="color: #ffffff;">Contact Phone</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """;">{}</td>""".format(Phone) + """
        </tr>
        <tr>
        <td style="background-color: """ + header_colour + """; "><span style="color: #ffffff;">Address</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """;">{}</td>""".format(Address) + """
        </tr>
        <tr>
        <td style="background-color: """ + header_colour + """;"><span style="color: #ffffff;">Zip Code</span></td>
        </tr>
        <tr>
        <td style="width: 100%;background-color: """ + data_colour + """;">{}</td>""".format(ZIPCode) + """
        </tr>
        </tbody>
        </table>
        """

        iframe = branca.element.IFrame(html=html, width=400, height=300)
        popup = folium.Popup(iframe, parse_html=True)
        postal_code = (df_contracts_found.loc[i, 'Zip Code'])
        location = nomi.query_postal_code(postal_code)
        lat = location.latitude
        lon = location.longitude
        points = [lat, lon]
        try:
            folium.Marker(
                points, tooltip=tooltip, popup=popup,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)

        except ValueError:
            print("Location unknown")

    # m.save("index.html")
    # webbrowser.open('index.html')
    return m.get_root().render()
