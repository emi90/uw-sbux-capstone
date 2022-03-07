# Dynamic Contextualization for Starbucks Orders
## University of Washington
## MS in Data Science
### Capstone Project

| Leena Elamrawy | Corina Geier   | Anant Rajeev   | Christie L. Gan | Emily Yamauchi |
|----------------|----------------|----------------|-----------------|----------------|
|[![LI][li-shield]][li-url_le]|[![LI][li-shield]][li-url_cg]|[![LI][li-shield]][li-url_ar]|[![LI][li-shield][li-url_clg]|[![LI][li-shield]][li-url_ey]|
|lelamraw@uw.edu|geiercc@uw.edu|anantr@uw.edu|clgan@uw.edu|eyamauch@uw.edu|

### Problem Statement

Starbucks deployed a new product recommendation system on their drive-thru screens at 4,000 Starbucks locations across the United States. 
The goal of this project is to redesign the recommendation system to include dynamic and contextual headlines to increase the conversation rate, 
thereby increasing sales and ultimately producing higher incremental tickets. 

### Solution

Our system predicts context labels to a requesting store based on conditions like the weather and the time of day. 
These context labels are then used to form potential headlines that would match these recommended products.    

Out of all the potential headlines, we picked the one that would give us the highest conversion rate. 
Our approach involved the use of reinforcement learning in the form of multi-armed bandits to determine the optimal headline choice.   

We were faced with the problem of a cold start (unsupervised learning) due to the lack of historical data regarding screen engagement with these newly generated headlines. 
To combat that, we adopted the Thompson Sampling algorithm, which uses a beta distribution as a parametric assumption to model the prior unknown distribution. 
The model recursively continues to learn and adjusts the reward model as a result.

### Data used:

#### ACTION REWARDS
Maps impressions to successful conversions
#### WEATHER
Normalized weather features per seasonality
#### STORE
Store level features such as number and location
#### PRODUCT
Product features such as product type, name, ingredients and flavor profile

### Project Goals

- Determine context labels to requesting store
- Predict optimal headline choice
- Ensure product recommendation alignment with chosen headline

### Feature Vectors

<p align="center">
  <img src="https://github.com/emi90/uw-sbux-capstone/blob/main/img/feature_vectors.png" />
</p>

<!-- MARKDOWN LINKS & IMAGES -->

[li-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[li-url_le]: https://www.linkedin.com/in/eyamauchi/
[li-url_cg]: https://www.linkedin.com/in/eyamauchi/
[li-url_ar]: https://www.linkedin.com/in/eyamauchi/
[li-url_cge]: https://www.linkedin.com/in/eyamauchi/
[li-url_ey]: https://www.linkedin.com/in/eyamauchi/