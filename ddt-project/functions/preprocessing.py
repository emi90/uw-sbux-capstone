import numpy as np
import pandas as pd

"""
Functions to preprocess stores dataframe
"""

def get_zipcodes_from_csv(df, url=None):
    """
    Function to get zipcodes from external csv file
    And add to stores dataframe
    df: pd.DataFrame
    url: url of csv file (on github)
    returns: pd.DataFrame
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

"""
Functions to preprocess weather dataframe
"""


def get_weather_state(snow, rain, hot, cold, temp_deseas, humid):
    """
    Define helper method that encodes the weather state appropriately
    """
    if rain==1:
        if snow==1: # rainy & snowy == snowy
            return 'snowy' 
        else:
            return 'rainy'
    if rain==1:
        return 'rainy'
    if cold==1:
        return 'chilly'
    if snow==1:
        return 'snowy'
    if snow==0:
        if rain==0:
            if temp_deseas > 0:
                return 'sunny'
            elif (hot==0) & (cold==0) & (humid==0):
                return 'pleasant'
    

"""
Functions to preprocess products dataframe
"""

import pandas as pd
import re


def get_valid_form_codes(df):
    """
    Function to clean the form codes in the product df
    Where product is a np.ndarray
    df: pd.DataFrame
    returns: pd.DataFrame
    """
    # Get rows where 'form_codes' value is not NA
    df_temp = df.loc[df.form_codes.isna()==False].copy()
    # Get first item in array if it only contains one form ("Iced" or "Hot")
    valid_codes = np.array([cds.item() if cds.shape[0]==1 
                            else "".join(cd for cd in cds) for cds in df_temp.form_codes])
    # Create a data frame with valid form codes
    valid_df = pd.DataFrame(data={'index':df_temp.index, 'valid_codes':valid_codes})
    df_merge = pd.merge(df.reset_index(), valid_df, how='left').drop(columns='index')
    
    return df_merge

def get_form_codes(df, iced_keywords):
    """
    Function to derive form codes from product names
    iced_keywords: list of iced keywords
    returns: pd.DataFrame
    """
    
    # Get valid form codes
    df_temp = get_valid_form_codes(df)
    
    # just the ones where form codes is None
    df_nans = df_temp.loc[(df_temp.valid_codes.isna()&(df_temp.productType=='Beverage'))].copy()
    
    # list of product names split at hyphen
    prod_name_list = [re.split(r'-', prod) for prod in df_nans.prod_num_name]
    codes_from_prod_name = ['Iced' if any(x in prds for x in iced_keywords) else 'Hot' for prds in prod_name_list]
    
    codes_df = pd.DataFrame(data={'index':df_nans.index, 'new_codes':codes_from_prod_name})
    df_merge = pd.merge(df_temp.reset_index(), codes_df, how='left').drop(columns='index')
    df_merge['new_codes'] = df_merge['new_codes'].fillna(df_merge['valid_codes'])
    
    return df_merge

def get_notional_flavor(df):
    """
    Function to derive NotionalFlavor from product names
    df: pd.DataFrame
    returns: pd.DataFrame
    """
    
    flavor_list = [prd.lower() for prd in df.NotionalFlavor.unique() if prd != None]

    # split at hyphen
    prod_name_list = [re.split(r'-', prod) for prod in df.prod_num_name]

    flv_from_prod = []
    for i, lst in enumerate(prod_name_list):
        temp_lst = [prd for prd in lst if prd in flavor_list]
        if len(temp_lst) > 0:
            temp_str = ','.join(temp_lst)
            flv_from_prod.append(temp_str)
        else:
            flv_from_prod.append(None)
    df['flavor_from_name'] = flv_from_prod
    
    return df