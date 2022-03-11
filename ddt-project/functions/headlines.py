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
    def __init__(self, store_df, product_df, weather_df, light_thres=0.5, sugar_thres=0.5, caff_thres=0.5, low_caff=50, mid_caff=100):
        """
        store_df: pd.DataFrame, dataframe for store data
        product_df: pd.DataFrame, dataframe for product data
        weather_df: pd.DataFrame, dataframe for weather data
        light_thres: calorie quartile for determining 'Light Pick Me Up', default=0.5
        sugar_thres: sugar quartile for determining 'Treat', default=0.5
        caff_thres: caffeine quartile for determining 'Boost', default=0.5
        low_caff: Caffeine threshold in mg for determining recommended caffeine vis-a-vis time of day, default=50
        mid_caff: Caffeine threshold in mg for determining recommended caffeine vis-a-vis time of day, default=100
        """
        self.store_df = store_df
        self.product_df = product_df
        self.weather_df = weather_df
        self.light_thres = light_thres
        self.sugar_thres = sugar_thres
        self.caff_thres = caff_thres
        self.low_caff=50
        self.mid_caff=100
    
    def set_sugar_thres(self, sugar_thres):
        self.sugar_thres=sugar_thres
    
    def set_light_thres(self, light_thres):
        self.light_thres=light_thres
    
    def set_caff_thres(self, caff_thres):
        self.caff_thres=caff_thres
    
    def set_low_caff(self, low_caff):
        self.low_caff=low_caff
    
    def set_mid_caff(self, mid_caff):
        self.mid_caff=mid_caff

    def __get_weather_state(self, snow, rain, hot, cold, temp_deseas, humid):
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

    def __get_weather_str(self, store_num, hour):
        """"
        Returns string of weather_state (i.e. sunny, chilly)
        """
        df = self.weather_df.copy()
        df['weather_state'] = df.apply(lambda x: self.__get_weather_state(
                                            x['ExtInd_SnowSumM95'], 
                                            x['ExtInd_RainSumM95'], 
                                            x['ExtInd_TempAvgDeseasM95'],
                                            x['ExtInd_TempAvgDeseasM05'], 
                                            x['TempAvgDeseas'], 
                                            x['ExtInd_TempHumidInteractDeseasM95']), axis=1)
        return df.loc[(df.StoreNumber==store_num)&(df.HourInDay==hour)]['weather_state'].item()

    def __get_daypart_str(self, hour):
        """
        Helper method to get daypart from hour
        """
        if hour < 11 and hour >= 3:
            return 'morning'
        elif hour < 14:
            return 'lunch'
        elif hour <= 17:
            return 'afternoon'
        else:
            return 'evening'


    def __get_store_city_str(self, store_num):
        """
        Helper method to get store city
        """
        df = self.store_df
        return df.loc[df['STORE_NUM'] == store_num]['city'].item()

    def __get_preferred_customer_modes(self, products):
        """
        Get modes from the given products
        returns: np dxn matrix (modes), and list of flavors
        """
        modes = np.zeros((3,len(products)))
        df = self.product_df.loc[self.product_df.prod_num_name.isin(products)].copy()
        # is_light
        modes[0] = np.where(df['avg_calories'] < df['avg_calories'].quantile(self.light_thres),1.0, 0.0)
        # is_treat
        modes[1] = np.where(df['avg_sugars_g'] > df['avg_sugars_g'].quantile(self.sugar_thres), 1.0, 0.0)
        # is_boost
        modes[2] = np.where(df['avg_caffeine_mg'] > df['avg_caffeine_mg'].quantile(self.caff_thres), 1.0, 0.0)
        # flavor
        flavor = [flv for flv in df.flavor_from_name if flv != None]
        form_codes = [cdes for cdes in df.new_codes if cdes != None]

        return modes, flavor, form_codes

    def __caffeine_thresholds(self, hour):
        """
        Helper method to get recommended caffeine threshold
        """
        if hour < 12:
            caffeine_thres = np.inf
        elif hour < 17:
            caffeine_thres = self.mid_caff
        else:
            caffeine_thres = self.low_caff
        return caffeine_thres
    
    def __assert_caffeine_validity(self, hour, products):
        """
        Helper method to check whether caffeiene level matches the time of day
        """
        df = self.product_df.loc[self.product_df.prod_num_name.isin(products)].copy().fillna(0)
        caffeine_levels = df['avg_caffeine_mg']
        caffeine_recs = self.__caffeine_thresholds(hour)
        is_valid = all(caffeine_levels <= caffeine_recs)
        #assert is_valid, "Exceeds recommended caffeine threshold"
        # any vs all
        return is_valid

    def __assert_form_codes(self, store_num, hour, products):
        """
        Helper method to check whether form code (iced, hot) matches the weather
        """
        form_codes = self.__get_preferred_customer_modes(products)[2]
        weather_state = self.__get_weather_str(store_num, hour)
        is_valid = False
        if weather_state == 'Sunny':
            is_valid = 'Hot' not in form_codes
            return is_valid
        elif weather_state == 'Chilly' or weather_state == 'Snowy' or weather_state == 'Rainy':
            is_valid = 'Iced' not in form_codes
            return is_valid
        #assert is_valid, "Drink type does not match weather recommendation"
        is_valid = True
        return is_valid
    
    def __get_customer_mode(self, products):
        """
        Helper method to get the list of customer modes
        """
        preferred_modes = self.__get_preferred_customer_modes(products)
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
        weather_state = self.__get_weather_str(store_num, hour).title()
        city = self.__get_store_city_str(store_num).title()
        daypart = self.__get_daypart_str(hour).title()
        #assert daypart != 'closed', "Store is closed"
        # this assert is taken out- MAB walkthru allowed 'closed' hours
        modes = self.__get_customer_mode(products)
        caffiene_validity = self.__assert_caffeine_validity(hour, products)
        form_validity = self.__assert_form_codes(store_num, hour, products)
        assert caffiene_validity, "Exceeds recommended caffiene threshold"
        assert form_validity, "Drink type does not match weather recommendation"

        # headlines
        headlines.append(f'{weather_state} in {city}')
        headlines.append(f'{daypart} in {city}')
        headlines.append(f'{weather_state} {daypart} in {city}')

        if len(modes) > 0:
            for mode in modes:
                mode_ = mode.title()
                headlines.append(f'{daypart} {mode_}')
                headlines.append(f'{weather_state} {mode_}')
        
        return headlines