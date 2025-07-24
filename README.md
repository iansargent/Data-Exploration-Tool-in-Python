# Vermont Livability Data Visualization App

A **Streamlit web app** for exploring, visualizing, and interpreting Vermont data. Users can upload one or more datasets and view tables, data summary reports, and custom plots through an interactive interface.

---


## Installation & Setup

1. **Clone** this repository:

   ```sh
   git clone https://github.com/your-username/vermont-livability.git
   cd vermont-livability
   ```

3. **Install** the package dependencies into an environment with python version <=3.11

   ```sh
   pip install -r requirements.txt
   ```

Or, if you have conda, use
```sh
conda env create -f environment.yml
```

4. **Run** the Streamlit app from the terminal with **this command**:

   ```sh
   streamlit run Home.py
   ```

---


## How to Use

1. **Launch** the app using this command in the terminal:

   ```sh
   streamlit run Home.py
   ```

2. **Upload** your data files via the sidebar. Many file formats are supported.
   
3. **Navigate** through the pages to preview, summarize, and visualize your data.

---

## Project File Structure

```
/vermont-livability-app
│── Home.py               # Main Streamlit app entry point
│── utils.py              # Helper functions for file uploads
│
├── pages/    # A "pages" folder to organize the different app pages
│   ├── 1_Table Preview.py    # Interactive data grid display (for uploaded files)
│   ├── 2_Data Summary.py     # Automated data quality and exploratory reports (for uploaded files)
│   ├── 3_Visualize.py        # Single + dual variable plotting, and group-by plotting (for uploaded files)
│   ├── 4_Zoning.py        # Mapping zoning regulations
│   ├── 5_Wastewater.py        # Mapping VT wastewater infrastructure
│   ├── 6_Housing.py        # Exploring Census housing data
│   ├── 7_Economics.py        # Exploring Census economic data
│   ├── 8_Demographics.py        # Exploring Census demographic data
│   ├── 9_Social.py        # Exploring Census social data
│   ├── 10_Flooding.py        # Mapping VT high risk flood zones (FEMA)
│   ├── 11_Mapping.py        # General mapping tool for uploaded geo files
│   └── 12_About.py            # App information and credits
│
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation
```

---

## License

This project is open-source under the **MIT License**.

---

## Credits

- Developed by Ian Sargent and Fitzwilliam Keenan-Koch
- Created under the Open Research Community Accelerator (ORCA) 
- Built using Streamlit and Python

---
