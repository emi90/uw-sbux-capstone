
import pandas as pd
import numpy as np

class HeadlineGenerator():
    """
    Create a set of 5 functions that create 5 headline variations.
    {weather_state} in {store_city} - 1 possible headline
    i.e. Sunny in Seatte
    {day_part} {preferred_customer_mode} - 4 possible headlines
    i.e. Afternoon Treat
    {weather_state} {preferred_customer_mode} - 4 possible headlines
    i.e. Pleasant Boost
    {daypart} in {store_city} - 1 possible headline
    i.e. Morning in Seattle
    {weather_state} {daypart} in {store_city} - 1 possible headline
    i.e. Sunny Morning in Seattle
    """
    def __init__(self, hour, store_num, products, store_df, product_df, weather_df):
        """
        hour: int, 0-23
        store_num: int, store number (given)
        products: list, 4 recommended products (given)
        store_df: pd.DataFrame, dataframe for store data
        product_df: pd.DataFrame, dataframe for product data
        weather_df: pd.DataFrame, dataframe for weather data
        """
        self.hour = hour
        self.store_num = store_num
        self.products = products
        self.store_df = store_df
        self.product_df = product_df
        self.weather_df = weather_df

    def get_weather_state(self, snow, rain, hot, cold, temp_deseas, humid):
        """
        Define helper method that encodes the weather state appropriately
        """
        if rain==1:
            if snow==1: # rainy & snowy == snowy
                return 'snowy'
            else:
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

    def get_weather_str(self):
        """"
        Returns string of weather_state (i.e. sunny, chilly)
        """
        df = self.weather_df.copy()
        df['weather_state'] = df.apply(lambda x: self.get_weather_state(
                                            x['ExtInd_SnowSumM95'], 
                                            x['ExtInd_RainSumM95'], 
                                            x['ExtInd_TempAvgDeseasM95'],
                                            x['ExtInd_TempAvgDeseasM05'], 
                                            x['TempAvgDeseas'], 
                                            x['ExtInd_TempHumidInteractDeseasM95']), axis=1)
        return df.loc[(df.StoreNumber==self.store_num)&(df.HourInDay==self.hour)]['weather_state'].item()

    def get_daypart_str(self):
        """
        Helper method to get daypart from hour
        """
        if self.hour > 6:
            if self.hour <= 11:
                return 'morning'
            elif self.hour <= 14:
                return 'lunch'
            elif self.hour <= 17:
                return 'afternoon'
            elif self.hour <= 22:
                return 'evening'
            else:
                return 'closed'
        else:
            return 'closed'

    def get_store_city_str(self):
        """
        Helper method to get store city
        """
        df = self.store_df
        return df.loc[df['STORE_NUM'] == self.store_num]['city'].item()

    def get_preferred_customer_modes(self, light_thres=0.5, sugar_thres=0.5, caff_thres=0.5):
        """
        Get modes from the given products
        returns: np dxn matrix (modes), and list of flavors
        """
        modes = np.zeros((3,len(self.prod_list)))
        df = self.product_df.loc[self.product_df.prod_num_name.isin(self.prod_list)].copy()
        # is_light
        modes[0] = np.where(df['avg_calories'] < df['avg_calories'].quantile(light_thres),1.0, 0.0)
        # is_treat
        modes[1] = np.where(df['avg_sugars_g'] > df['avg_sugars_g'].quantile(sugar_thres), 1.0, 0.0)
        # is_boost
        modes[2] = np.where(df['avg_caffeine_mg'] > df['avg_caffeine_mg'].quantile(caff_thres), 1.0, 0.0)
        # flavor
        flavor = [flv for flv in df.NotionalFlavors if flv != None]
        form_codes = [cdes for cdes in df.FormCodes if cdes != None]

        return modes, flavor, form_codes

    def caffeine_thresholds(self, low=50, mid=100):
        """
        Helper method to get recommended caffeine threshold
        """
        if self.hour < 12:
            caffeine_thres = np.inf
        elif self.hour < 17:
            caffeine_thres = mid
        else:
            caffeine_thres = low
        return caffeine_thres
    
    def assert_caffeine_validity(self):
        """
        Helper method to check whether caffeiene level matches the time of day
        """
        caffeine_levels = self.product_df.loc[self.product_df.prod_num_name.isin(self.prod_list)].copy()['avg_caffeine_mg']
        caffeine_recs = self.caffeine_thresholds()
        is_valid = caffeine_levels <= caffeine_recs
        #assert is_valid, "Exceeds recommended caffeine threshold"
        return is_valid

    def assert_form_codes(self):
        """
        Helper method to check whether form code (iced, hot) matches the weather
        """
        form_codes = self.get_preferred_customer_modes()[2]
        weather_state = self.get_weather_str()
        if weather_state == 'Sunny':
            is_valid = 'Hot' not in form_codes
        elif weather_state == 'Chilly' or 'Snowy' or 'Rainy':
            is_valid = 'Iced' not in form_codes
        #assert is_valid, "Drink type does not match weather recommendation"
        return is_valid
    
    def get_customer_mode(self):
        """
        Helper method to get the list of customer modes
        """
        preferred_modes = self.get_preferred_customer_modes()
        customer_mode = preferred_modes[0]
        flavors = preferred_modes[1]
        modes = []
        if customer_mode[0].sum() > 0: # is_light
            modes.append('Light Pick Me Up')
        if customer_mode[1].sum() > 0: # is_treat
            modes.append('Treat')
        if customer_mode[2].sum() > 0: # is_boost
            modes.append('Boost')
        if len(flavors) > 0: # flavors
            modes.append('Flavor')
        return modes

    
    def get_headlines(self):
        """
        Method to get the list of headlines given the product list, time of day, and store number
        """
        headlines = []
        weather_state = self.get_weather_str()
        city = self.get_store_city_str()
        daypart = self.get_daypart_str()
        modes = self.get_customer_mode()
        caffiene_validity = self.assert_caffeine_validity()
        form_validity = self.assert_form_codes()
        assert caffiene_validity, "Exceeds recommended caffiene threshold"
        assert form_validity, "Drink type does not match weather recommendation"

        # headlines
        headlines.append(f'{weather_state} in {city}')
        headlines.append(f'{daypart} in {city}')
        headlines.append(f'{weather_state} {daypart} in {city}')

        if len(modes) > 0:
            for mode in modes:
                headlines.append(f'{daypart} {mode}')
                headlines.append(f'{weather_state} {mode}')
        
        return headlines

