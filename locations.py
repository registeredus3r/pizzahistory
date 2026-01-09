# Pentagon Pizza Index - Locations Configuration
# All target locations with their Google Maps URLs

LOCATIONS = [
    # Pentagon Area (Arlington, VA) - Data from pizzint.watch
    {
        "id": "pentagon_dominos",
        "name": "Domino's Pizza",
        "area": "Pentagon",
        "pizzawatch_id": "ChIJI6ACK7q2t4kRFcPtFhUuYhU",
        "url": "https://www.google.com/maps/place/Domino's+Pizza/@38.8627308,-77.0879692,17z"
    },
    {
        "id": "pentagon_extreme_pizza",
        "name": "Extreme Pizza",
        "area": "Pentagon",
        "pizzawatch_id": "ChIJcYireCe3t4kR4d9trEbGYjc",
        "url": "https://www.google.com/maps/place/Extreme+Pizza/@38.8602396,-77.0585603,17z"
    },
    {
        "id": "pentagon_we_the_pizza",
        "name": "We, The Pizza",
        "area": "Pentagon",
        "pizzawatch_id": "ChIJS1rpOC-3t4kRsLyM6aftM8k",
        "url": "https://www.google.com/maps/place/We,+The+Pizza/@38.8663614,-77.0588449,15.76z"
    },
    {
        "id": "pentagon_district_pizza",
        "name": "District Pizza Palace",
        "area": "Pentagon",
        "pizzawatch_id": "ChIJ42QeLXu3t4kRnArvcaz2o3A",
        "url": "https://www.google.com/maps/place/District+Pizza+Palace/@38.8527414,-77.0531408,17z"
    },
    {
        "id": "pentagon_papa_johns",
        "name": "Papa John's Pizza",
        "area": "Pentagon",
        "pizzawatch_id": "ChIJo03BaX-3t4kRbyhPM0rTuqM",
        "url": "https://www.google.com/maps/place/Papa+Johns+Pizza/@38.8292633,-77.1901741,11.83z"
    },
    {
        "id": "pentagon_pizzato",
        "name": "Pizzato Pizza",
        "area": "Pentagon",
        "pizzawatch_id": "ChIJrbin_Qm3t4kRVSytw_2DM1g",
        "url": "https://www.google.com/maps/place/Pizzato+Pizza/@38.8791607,-77.096414,15.18z"
    },
    {
        "id": "pentagon_freddies_beach",
        "name": "Freddie's Beach Bar & Restaurant",
        "area": "Pentagon",
        "type": "inverse",
        "pizzawatch_id": "ChIJlxXYvim3t4kR4MCE7Wn3AqI",
        "url": "https://www.google.com/maps/place/Freddie's+Beach+Bar+%26+Restaurant/@38.8535526,-77.0597718,17z"
    },
    {
        "id": "pentagon_little_gay_pub",
        "name": "The Little Gay Pub",
        "area": "Pentagon",
        "type": "inverse",
        "pizzawatch_id": "ChIJSVAJ-5O3t4kRB43eiub4BqM",
        "url": "https://www.google.com/maps/place/The+Little+Gay+Pub/@38.9094961,-77.0298976,17z"
    },
    
    # Mar-a-Lago Area (West Palm Beach, FL) - Data from BestTime.app
    {
        "id": "maralago_lynoras",
        "name": "Lynora's",
        "address": "3301 S Dixie Hwy, West Palm Beach, FL 33405",
        "area": "Mar-a-Lago",
        "url": "https://www.google.com/maps/place/Lynora's/@26.7056,-80.0364,17z"
    },
    {
        "id": "maralago_pizza_de_roma",
        "name": "Pizza De Roma",
        "address": "5614 S Dixie Hwy, West Palm Beach, FL 33405",
        "area": "Mar-a-Lago",
        "url": "https://www.google.com/maps/place/Pizza+De+Roma/@26.7072,-80.0356,17z"
    },
    {
        "id": "maralago_taste_of_italy",
        "name": "Taste of Italy",
        "address": "6920 S Dixie Hwy, West Palm Beach, FL 33405", # Verified address would be better
        "area": "Mar-a-Lago",
        "url": "https://www.google.com/maps/place/Taste+of+Italy/@26.6881,-80.0364,17z"
    },
    
    # CIA Area - Disabling for now as user only specified Pentagon and Mar-a-Lago via APIs
    # Control Locations - Disabling for now
]
