# Seattle-Accessory-Dwelling-Units
This repository seeks to explore the current status of Attached Accessory Dwelling Units (AADUs) and Detached Accessory Dwelling Units (DADUs) in Seattle over time.

## Contributor(s)
Tyler Bonnell 

## Description
With the meteroic rise in housing prices, new solutions to increase the housing stock (as well as the value of one's property) are being explored tested. In recent years, the Accessory Dwelling Unit (ADUs) is one solution that has gained popularity due to its relative low cost and space requirements. Accessory Dwelling Units can be categorized broadly based on whether the units are 1) attached (Attached Accessory Dwelling Units or AADUs) or are 2) detached (Detached Accessory Dwelling Units or DADUs) to a pre-existing home. 

Seattle is an excellent microcosm to examine the utility and promise of Accessory Dwelling Units as one method to increase the housing inventory because:
- Seattle is among the most expensive real-estate markets in the United States (In 2023, [Kiplinger rated Seattle as the 12th most expensive real estate market in the United States](https://www.kiplinger.com/real-estate/603612/15-us-cities-with-the-highest-average-home-prices) with an average home price of $ 937,623).
- In September 2020, the City of Seattle launched the [ADUniverse](https://aduniverse-seattlecitygis.hub.arcgis.com/), an online hub with guides to building ADUs, a locator tool to determine if a property is eligible to build a ADU on (per city code), as well as pre-approved ADU plans. In short, they have greatly streamlined the administrative and bureaucratic process to begin building an ADU in the city. 

Through this repository, I am seeking to explore the trends of ADU permitting, construction, and utilization in Seattle over time using open source data from the [City of Seattle Open Data Portal](https://data.seattle.gov/). 

### Analysis Questions
- How has the number of 1) ADU permits and 2) ADU units built changed over time? Was there a significant increase after the launch of the ADUniverse? 
- Has the process of reviewing and deciding on permit status speed up after the launch of ADUniverse?
- What regions (neighborhoods, council districts) have the greatest number of ADUs? 
- In 2023, were AADUs or DADUs the more popular? 

### Skills Learned:
- String (with regex), DateTime, and Categorical variable manipulation.
- .apply() -- Cleaning multiple variables using single operations.
- zipping lists into dictionaries --> to rename columns in pandas data frames.
- Cenpy -- Pulling Census Data via API and joining data to pandas data frames. 
- Feather -- Storing data in a universal format with fast read/write times using Apache Spark.