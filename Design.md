

# Overall Vision
The Vermont Data Collaborative portal is a website with three main pieces of functionality: data storage and access, data training, and data analysis. Designed in close partnership with stakeholders in the private sector, professional goverment, and citizen government, it aims to help Vermonters find and use the data they need to make their work easier and more effective. 


## Feedback and Outreach Strategy
1. First, a prototype of the website is built in streamlit, focusing on the core data visualization features. Ad-Hoc individual feedback sessions with community leaders (RPC heads, VLCT heads) and conversational statements of interest drive functionality. 
2. Next, the prototype is reviewed by UVM faculty and workers


# Architecture
The website consists of two containerized modules--a backend for data processing and a frontend for a user interface and display -- as well as data storage and 

## Frontend
The frontend is a javascript website designed for easy use by a non-technical user. 
### Stack
`React` and `Next.js` do the majority of the work, with additional custom html and css along the edges. We may include some `D3.js` if others write it, too. 

### Functionality
* trainings and video walkthroughs for how to use it 
* feedback and data requests
* exploratory data visualization and low-level analysis, including exports
* raw data exports 
* customizable auto-generated reports for counties, RPCs, and municipalities, both general and by subject area.

### User Interface
* Navigation
* Dashboards
* Interactive Maps 
* Report generation and customization (ability to add user created visuals into report seamlessly)

## Backend
The backend for the website consists largely of data manipulation in python. 

### Stack
Python: FastAPI, pandas, geopands, pyogrio

### Functionality
* Data Processing
* Filtering
* serving JSON/GeoJSON


## Database
