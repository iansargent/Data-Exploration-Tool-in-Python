# Overall Vision
The Vermont Data Collaborative portal is a website with three main pieces of functionality: data storage and access, data training, and data analysis. Designed in close partnership with stakeholders in the private sector, professional government, and citizen government, it aims to help Vermonters find and use the data they need to make their work easier and more effective.
## Rollout Steps
1. VERSO students build a prototype of the portal in streamlit (python), focusing on the core data visualization features. Ad-Hoc individual feedback sessions with community leaders (RPC heads, VLCT heads) and conversational statements of interest drive initial functionality.
2. UVM faculty and SMEs review and update a stable version of the prototype and begin more detailed design of the eventual final version.
3. The advisory council review the stable prototype, with an emphasis on potential indicators of interest and key functionality going forward.
4. VERSO students collate and organize feedback and confer with UVM faculty and SMEs
5. VERSO students begin work on second version of product, now built in javascript.
6. Second round of feedback... 
7. Continue iterating on product...
8. Broader go live....
9. VERSO students organize SOPs for updates and maintenance in the future.

## Technical Steps
##### Phase 1: prototyping
1. Rough prototyping in streamlit
2. Modularize streamlit; improve caching speed and add additional functionality
3. Begin decoupling front-end and back-end
---- Feedback

#### Phase two: local host
1. Construct initial setup of frontend (without data) on local host.
2. Fully integrate fastAPI into backend, hooking up test connections to frontend as you go.
3. Replicate all prototype functionality (with feedback improvements) on javascript local host
4. Add additional functionality that javascript affords: multi-layer mapping, exporting
5. Bugfixes, render stable version
---- Feedback

#### Phase three: server
1. Containerize and test containers on local host.
2. Acquire server, set up SSH and basic infrastructure
3. migrate code to server and setup dockers, etc.
4. stability and bughunt 
---- QA and additional feedback
5. Go live
6. Organize SOPs for maintenance

#### Phase four: extensions and maintenance
* update caching
* update database (see below)
* allow for user uploads
* add additional requested functionality

# Main Architecture
The website consists of two containerized modules--a backend for data processing and a frontend for a user interface and display. 
## Frontend
The frontend is a javascript website designed for easy use by a non-technical user.
#### Stack
`React` and `Next.js` do the majority of the work, with additional custom html and css along the edges. We may include some `D3.js` if others write it, too.
#### Functionality
* trainings and video walkthroughs for how to use it
* feedback and data requests
* exploratory data visualization and low-level analysis, including exports
* raw data exports
* customizable auto-generated reports for counties, RPCs, and municipalities, both general and by subject area.
* working with separate data areas in the same interface (eg, mapping).
	* including filtering
#### User Interface
* Navigation
* Dashboards
* Interactive Maps
* Report generation and customization (ability to add user created visuals into report seamlessly)
* Clear data sourcing and caveats concerning quality
## Backend
The backend for the website consists largely of data manipulation in python.
#### Stack
Python: FastAPI, pandas, geopandas, pyogrio
#### Functionality
* Data cleaning and processing
* Data filtering from frontend requests
* serving JSON/GeoJSON to frontend
* ability to cleanly include new data sources
* allow cross-referencing between datasets based on
	* geography: intersection, containment, etc.
	* names: codes, full names
####  Optimization
If performance becomes a concern, VERSO students take the following actions:
- improve backend caching: use the `moka.py` library.
- upgrade the database querying: switch from csv files to a postgreSQL database (see below)


# Supporting Architecture

##  Database
#### Phase one
- Data stored as CSV, parquet, FGB, or GeoJSON on a mounted volume accessible to the backend container
- Automatic update scripts handle cleaning, versioning, and validation
- Organized by data domain with accompanying metadata
#### Phase two (optional)
- Data stored in PostgreSQL/PostGIS for scalable, queryable storage
- Backend queries database instead of reading files directly
- Designed later, if required\
## Containerization
- The frontend and backend are containerized using Docker Compose. 
- These containers are built on a server, probably AWS, using SSH

## Security 
- Server accessed via SSH only
- containers isolated; no direct access to external data
- open source data eliminated need for user authentication


# Miscellaneous Comments
## Authorization and Access
All data is intended to be open source and fully accessible. This both meets open source goals, meets public interest, and makes our jobs easier by not having to implement authorization protocols, etc. 

## Maintenance and Updates
Because there are no user roles, e.g., administrators, all maintenance and updates must be done in a coding environment. This puts an extra emphasis on making the code as modular, extensible, and clear as possible. In addition, VERSO students and SMEs will put together SOPs for maintenance and updates for future staff. 


# Extensions
## User uploaded data
This the additional work and extensions required to securely allow user uploads for temporary sessions. 
- **Backend**
    - Create an endpoint in FastAPI to accept file uploads.
    - Validate file type, size, and structure before processing.
    - Isolate each user’s upload in a separate folder or temporary storage. Does not go to database.
    - limit file size -- just goes in cache, we don't stor
- **Database**
    - Data is not stored in central database.
- **Security**
    - Sanitize file names and paths.
    - Limit executable content to prevent code injection.
    - Optionally run processing in a sandboxed environment or container.
- **UI**
    - Provide a simple “Upload Data” form.
    - Show feedback if the upload fails or data is invalid.
    - Allow users to interact with their data alongside portal datasets.
- **Containerization**
	-  HTTPS: 
		- Run a reverse proxy in front of Docker containers (caddy)
		- Obtain SSL certificate
		- route all HTTP traffic to HTTPS