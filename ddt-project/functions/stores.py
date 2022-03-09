"""
Functions to preprocess stores dataframe
"""

import pandas as pd

def get_zipcodes_from_csv(df, url=None):
    """
    Function to get zipcodes from external csv file
    And add to stores dataframe
    df: pd.DataFrame
    url: url of csv file (on github)
    """
    
    # get raw csv file from github unless specified
    if url is not None:
        geodata_link = url
    else:
        geodata_link = 'https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv'
    geo_data = pd.read_csv(geodata_link)
    
    # need to keep in str format for leading zeros- but drop zipcodes that can't coerce to ints
    geo_data['zip_int'] = geo_data.zipcode.apply(lambda x: pd.to_numeric(x, errors='coerce'))
    geo_df = geo_data.dropna()
    
    # merge with df
    store_city_df = pd.merge(df, geo_df[['city','state','zipcode']], 
                        how='left',
                        left_on='zipOrPostalCode',
                        right_on='zipcode').drop(columns=['zipcode'])
    
    return store_city_df