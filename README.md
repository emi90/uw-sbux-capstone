# Dynamic Contextualization for Starbucks Orders
## University of Washington
## MS in Data Science
### Capstone Project

| Leena Elamrawy | Corina Geier   | Anant Rajeev   | Christie L. Gan | Emily Yamauchi |
|----------------|----------------|----------------|-----------------|----------------|
|[![LI][li-shield]][li-url_le]|[![LI][li-shield]][li-url_cg]|[![LI][li-shield]][li-url_ar]|[![LI][li-shield]][li-url_clg]|[![LI][li-shield]][li-url_ey]|
|lelamraw@uw.edu|geiercc@uw.edu|anantr@uw.edu|clgan@uw.edu|eyamauch@uw.edu|

### Problem Statement

Starbucks deployed a new product recommendation system on their drive-thru screens at 4,000 Starbucks locations across the United States. 
The goal of this project is to redesign the recommendation system to include dynamic and contextual headlines to increase the conversation rate, 
thereby increasing sales and ultimately producing higher incremental tickets. 

### Solution

Our system predicts context labels to a requesting store based on conditions like the weather and the time of day. 
These context labels are then used to filter through potential headlines that would match these recommended products.    

Out of all the potential headlines, we picked the one that would give us the highest conversion rate. 
Our approach involved the use of reinforcement learning in the form of multi-armed bandits to determine the optimal headline choice.   

We were faced with the problem of a cold start (unsupervised learning) due to the lack of historical data regarding screen engagement with these newly generated headlines. 
To combat that, we adopted the Thompson Sampling algorithm, which uses a beta distribution as a parametric assumption to model the prior unknown distribution. 
The model recursively continues to learn and adjusts the reward model as a result.

### Data used:

#### ACTION REWARDS
- Maps impressions to successful conversions
#### WEATHER
- Normalized weather features per seasonality
#### STORE
- Store level features such as number and location
#### PRODUCT
- Product features such as product type, name, ingredients and flavor profile

### Project Goals

- Determine context labels to requesting store
- Predict optimal headline choice
- Ensure product recommendation alignment with chosen headline

### Assumptions

Below are some of the assumptions and thresholds that were set for this project.
- Cold drinks are not recommended for cold days and hot drinks are not recommended for hot days
- Caffeine thresholds were set at 50mg or lower for a low caffeine drink, and 50 to 100mg for a mid level caffeinated drink
- "Pleasant" weather state was defined if the weather state was not rainy, snowy, hot, cold, or humid
- "Sunny" weather was defined if it was not rainy, snowy and the deseasonalized temperature was above 0
- Morning hours were set between 3am and 11am, lunch between 11am and 2pm, afternoon between 2pm to 5pm and evening between 5pm and 3am
- 12pm to 5pm allows for mid level caffienated drinks, and 5pm to midnight assumes low caffeine drink recommendations
- Sugar thresholds for defining a product as a "Treat" is set at a default of containing above the average amount of sugar 
- Caffeine thresholds for determining if a product was a "Boost" or not is set at a default of containing above the average amount of caffeine
- A "Light Pick Me Up" product was defined as containing below the average amount of calories from the product list.

### Feature Vectors

<p align="center">
  <img src="https://github.com/emi90/uw-sbux-capstone/blob/main/img/feature_vectors.png" />
</p>

### Multi-Armed Bandits

The multi-armed bandit problem models an agent that wants to simultaneously acquire new knowledge (exploration) and optimize decisions based on existing knowledge (exploitation). 

The information (customers purchasing the recommended products or not) gained from the data gathered will shift the distribution in different ways to reflect an accurate reward model. 

The model recursively continues to learn about which headlines are contributing to a higher conversion rate. This then allows Starbucks to make a store-by-store decision with regards to which headlines they want to display on that drive-thru. 



<!-- MARKDOWN LINKS & IMAGES -->

[li-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[li-url_le]: https://www.linkedin.com/in/leena-elamrawy
[li-url_cg]: https://www.linkedin.com/in/corina-geier
[li-url_ar]: https://www.linkedin.com/in/anant-rajeev-95687a128
[li-url_clg]: https://www.linkedin.com/mwlite/in/christie-lee-gan-33a12a12a
[li-url_ey]: https://www.linkedin.com/in/eyamauchi/
