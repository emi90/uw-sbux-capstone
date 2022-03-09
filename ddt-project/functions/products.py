"""
Functions to preprocess products dataframe
"""

import pandas as pd
import re

def get_valid_form_code(df, ice_keywords):
    """
    Function to identify correct valid form codes from the product table
    Will identify "Beverage" and None items as "iced" or None
    and update form codes column in  "Updated_form_codes"
    df: pd.Dataframe
    ice_keywords: list of keywords of iced drinks (refreshers, frappuccino, etc.)
    returns: pd.DataFrame
    """
    
    # filter on rows that are beverages and rows that are None
    df = df.loc[df.productType=='Beverage']
    df = df.loc[df.form_codes.isna()]
    
    # original product list
    prod_name_list = [re.split(r'-', prod) for prod in df.prod_num_name]
    
    # select all rows that are beverages & where there is no form_code
    bev_products_none_form_codes = df.loc[(df.productType=='Beverage')&(df.form_codes.isna())]['prod_num_name'] 
    bev_products_none_form_codes_lst = [re.split(r'-', prod) for prod in bev_products_none_form_codes]
    iced_no_iced_lst = []
    for i in bev_products_none_form_codes_lst:
        if any(x in i for x in ice_keywords):
            iced_no_iced_lst.append('Iced')
        else:
             iced_no_iced_lst.append(None) ## CHECK: do we want nonetype or str none??
                
    # create dictionary with keys as products and values as iced_no_iced_lst/form_code
    bev_products_none_form_codes_to_list = list(bev_products_none_form_codes)
    res = {bev_products_none_form_codes_to_list[i]: iced_no_iced_lst[i] for i in range(len(bev_products_none_form_codes_to_list))}
    
    # use dictionary to map new form codes to products
    df['Updated_form_codes'] =df.prod_num_name.map(res)
    
    return df


def get_caffeine_recs(hour):
    """
    Function to return recommended caffeine in mg given hour
    hour: int, hour of day in 0-23
    returns: int, mg of caffeine
    """
    if hour < 12:
        return np.inf
    elif hour < 17:
        return 100
    else:
        return 50
    
def get_item_caffeine(df, hour):
    """
    Function to return subset of product dataframe given hour for appropriate caffeine levels
    df: pd.DataFrame
    hour: int, hour of day in 0-23
    """
    caffeine_level = get_caffeine_recs(hour)
    # return > level ==False, to account for np.nans
    return df.loc[(df.avg_caffeine_mg>caffeine_level)==False]


def filter_headlines(df, prod_list, headline_list):
    """
    Function to filter the headliens at a particular store
    based on the products that they recommend
    """
    final_list = []
    for prod in prod_list:
        product_information = df[df['prod_num_name']==prod].reset_index()
        if product_information['is_light'][0] == 'Light Pick Me Up':
            final_list.extend([headline for headline in headline_list if "Light Pick Me Up"  in headline])
        if product_information['is_treat'][0] == 'Treat':
            final_list.extend([headline for headline in headline_list if "Treat" in headline])
        if product_information['is_boost'][0]== 'Boost':
            final_list.extend([headline for headline in headline_list if "Boost"  in headline]) 
    return set(final_list)



