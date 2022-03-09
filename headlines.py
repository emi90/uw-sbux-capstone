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
    def __init__(self, store_df, product_df, weather_df):
        """
        store_df: pd.DataFrame, dataframe for store data
        product_df: pd.DataFrame, dataframe for product data
        weather_df: pd.DataFrame, dataframe for weather data
        """
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

    def get_weather_str(self, store_num, hour):
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
        return df.loc[(df.StoreNumber==store_num)&(df.HourInDay==hour)]['weather_state'].item()

    def get_daypart_str(self, hour):
        """
        Helper method to get daypart from hour
        """
        if hour > 6:
            if hour <= 11:
                return 'morning'
            elif hour <= 14:
                return 'lunch'
            elif hour <= 17:
                return 'afternoon'
            elif hour <= 22:
                return 'evening'
            else:
                return 'closed'
        else:
            return 'closed'

    def get_store_city_str(self, store_num):
        """
        Helper method to get store city
        """
        df = self.store_df
        return df.loc[df['STORE_NUM'] == store_num]['city'].item()

    def get_preferred_customer_modes(self, products, light_thres=0.5, sugar_thres=0.5, caff_thres=0.5):
        """
        Get modes from the given products
        returns: np dxn matrix (modes), and list of flavors
        """
        modes = np.zeros((3,len(products)))
        df = self.product_df.loc[self.product_df.prod_num_name.isin(products)].copy()
        # is_light
        modes[0] = np.where(df['avg_calories'] < df['avg_calories'].quantile(light_thres),1.0, 0.0)
        # is_treat
        modes[1] = np.where(df['avg_sugars_g'] > df['avg_sugars_g'].quantile(sugar_thres), 1.0, 0.0)
        # is_boost
        modes[2] = np.where(df['avg_caffeine_mg'] > df['avg_caffeine_mg'].quantile(caff_thres), 1.0, 0.0)
        # flavor
        flavor = [flv for flv in df.flavor_from_name if flv != None]
        form_codes = [cdes for cdes in df.new_codes if cdes != None]

        return modes, flavor, form_codes

    def caffeine_thresholds(self, hour, low=50, mid=100):
        """
        Helper method to get recommended caffeine threshold
        """
        if hour < 12:
            caffeine_thres = np.inf
        elif hour < 17:
            caffeine_thres = mid
        else:
            caffeine_thres = low
        return caffeine_thres
    
    def assert_caffeine_validity(self, hour, products):
        """
        Helper method to check whether caffeiene level matches the time of day
        """
        df = self.product_df.loc[self.product_df.prod_num_name.isin(products)].copy().fillna(0)
        caffeine_levels = df['avg_caffeine_mg']
        caffeine_recs = self.caffeine_thresholds(hour)
        is_valid = all(caffeine_levels <= caffeine_recs)
        #assert is_valid, "Exceeds recommended caffeine threshold"
        # any vs all
        return is_valid

    def assert_form_codes(self, store_num, hour, products):
        """
        Helper method to check whether form code (iced, hot) matches the weather
        """
        form_codes = self.get_preferred_customer_modes(products)[2]
        weather_state = self.get_weather_str(store_num, hour)
        if weather_state == 'Sunny':
            is_valid = 'Hot' not in form_codes
        elif weather_state == 'Chilly' or 'Snowy' or 'Rainy':
            is_valid = 'Iced' not in form_codes
        #assert is_valid, "Drink type does not match weather recommendation"
        return is_valid
    
    def get_customer_mode(self, products):
        """
        Helper method to get the list of customer modes
        """
        preferred_modes = self.get_preferred_customer_modes(products)
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

    
    def get_headlines(self, store_num, hour, products):
        """
        Method to get the list of headlines given the product list, time of day, and store number
        """
        headlines = []
        weather_state = self.get_weather_str(store_num, hour)
        city = self.get_store_city_str(store_num)
        daypart = self.get_daypart_str(hour)
        assert daypart != 'closed', "Store are closed"
        modes = self.get_customer_mode(products)
        caffiene_validity = self.assert_caffeine_validity(hour, products)
        form_validity = self.assert_form_codes(store_num, hour, products)
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