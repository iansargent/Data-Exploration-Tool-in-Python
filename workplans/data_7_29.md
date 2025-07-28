
Workplan for Mon Jul 28 10:27:45 EDT 2025

FITZ
* [ ] General Refactor -- functionalize throughout, particularly in zoning, wastewater, and flooding
    * Add in wastewater service areas
* [ ] Single Mapping Page
    * [ ] Standardize filtering and ui for zoning, wastewater, flooding
    * [ ] Turn functions into multi-layering ones / wrap them in such 
    * [ ] Integrate into a single pydeck for a rough compare page
    * plan ahead -- dictionary for different type of data (eg, polygon, point)
* Ideas for contacts about budgetary planning / budgetary data 
* Stretches 
    * Report -- social and demographics
    * Integrate census data into the rough compare page 

IAN: 
* Getting better wastewater service areas
    * Load in wastewater service areas
    * general  town boundaries function
* Economics Report and Zoning Report

BOTH: 
research / look into setting up the data pipeline

LATER 
* [ ] Pipeline Improvements
    * [ ] Initial Build: (and, later, scheduled update jobs):
        * Really what this is just to automate as much as possible getting the census data; generally getting all the data into a common set that we can easily pull from (eg, SQL databases set up with the same structure)
        * [ ] Setup APIs (farther ranging)
        * [ ] Cache into SQL
    * [ ] Load:
        * [ ] Check *dated* cache @ github
        * [ ] fallback to APIs if load fails
* [ ] Loading throughout via single pipeline / dictionary