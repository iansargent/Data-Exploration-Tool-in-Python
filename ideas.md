# Functional Improvements

### New Census Comparison Page
- [ ] Year selection for base and comparison datasets
- [ ] Bar chart sorting (ascending, descending, alphabetical, etc.)
- [X] Show tabular data feature with Excel download button
- [ ] Migrate filters off of main page (likely not implemented while using streamlit)
- [ ] Dual scroll mechanism in side by side comparison with middle separator
        --ooh, I like this. -FJK

### Zoning Page
- [X] Separate mapping, area stats, and law comparisons into three separate tabs
- [X] Do not load the zoning dataset until geographic filters are selected (to speed up map rendering time)
- [X] Find better way for district selection for comparison (Get rid of Aggrid Select Table)

### Budgeting Data
- [ ] Decide if we need data upload feature
- [ ] Link to possible [VT Finance Data](https://data.vermont.gov/Government/Town-Payment-Report/ud6m-kdia/about_data?_gl=1*haczy7*_ga*MTg0MzI5MzkyOC4xNzQ3NzQ3NTM3*_ga_V9WQH77KLW*czE3NTMxOTk1MDIkbzE1JGcxJHQxNzUzMTk5NTU1JGo3JGwwJGgw)

### Census Mapping Tab
- [ ] Add "Top/Bottom Ten" tables for the mapped variable


## Coding Improvements and refafctoring
- [ ] Create a central dictionary (via a class) that holds all the data we'll use imported. then just grab them from there rather than copying and pasting names. Also means we have one central location to change import / cleaning logic, etc. 
- [ ] In general, functionalize and modularize throughout. Remove as many if/else as possible; replace with dictionaries and more extensible behavior.
- [ ] Set up a PostGreSQL Database to house all datasets in a relational model. Allows for spatial joins + complex queries using `st.connection()`

# TODOs
* [ ] Rename Jurisdiction to Municipality throughout
