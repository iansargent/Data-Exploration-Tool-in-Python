# Vermont Livability Data Visualization App

A **Streamlit web app** for exploring, visualizing, and interpreting Vermont data. Users can upload one or more datasets and view tables, data summary reports, and custom plots through an interactive interface.

---


## Installation & Setup

1. **Clone** this repository:

   ```sh
   git clone https://github.com/your-username/vermont-livability.git
   cd vermont-livability
   ```

3. **Install** the package dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. **Run** the Streamlit app** from the terminal with **this command**:

   ```sh
   streamlit run Home.py
   ```

---


## How to Use

1. **Launch the app using this command in the terminal:**

   ```sh
   streamlit run Home.py
   ```

2. **Upload your data files via the sidebar. Many file formats are supported.**

   * Insert Screenshot
   
3. **Navigate through the pages to preview, summarize, and visualize your data.**

---


## Some Features


- ✅ **Upload** and **preview** CSV, Excel, JSON, or SPSS datasets

- ✅ Interactive data **table display**

- ✅ Layered **mapping** with geojson files

- ✅ Automated **data profiling** and **summary statistics**

- ✅ **Visualization** for single variables and variable pairs

- ✅ An **About Page** to learn more about this project

---


## Project File Structure

```
/vermont-livability-app
│── Home.py               # Main Streamlit app entry point
│── utils.py              # Helper functions for file uploads
│
├── pages/    # A "pages" folder to organize the different app pages
│   ├── 1_Table Preview.py    # Interactive data grid display
│   ├── 2_Data Summary.py     # Automated data profiling and summaries
│   ├── 3_Visualize.py        # Single and dual variable plotting
│   └── 4_About.py            # App information and credits
│
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation
```

---

## Planned Improvements

- Add data comparison support features (for VT jurisdictions)
- Include interactive geospatial mapping
- Include filtering 
- Improved UX and overall app design

---

## License

This project is open-source under the **MIT License**.

---

## Credits

- Created by Ian Sargent  
- Developed under the Open Research Community Accelerator  
- Built with Streamlit and Python

---

### Enjoy & Have Fun Exploring!
