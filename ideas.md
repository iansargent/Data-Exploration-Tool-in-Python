# Functional Improvements

### New Census Comparison Page
- [ ] Year selection for base and comparison datasets
- [ ] Bar chart sorting (ascending, descending, alphabetical, etc.)
- [ ] Show tabular data feature with Excel download button
- [ ] Migrate filters off of main page (likely not implemented while using streamlit)
- [ ] Dual scroll mechanism in side by side comparison with middle separator
        --ooh, I like this. -FJK

### Zoning Page
- [ ] Separate mapping, area stats, and law comparisons into three separate tabs
- [ ] Do not load the zoning dataset until geographic filters are selected (to speed up map rendering time)


## Coding Improvements and refafctoring
- [ ] Create a central dictionary (via a class) that holds all the data we'll use imported. then just grab them from there rather than copying and pasting names. Also means we have one central location to change import / cleaning logic, etc. 
- [ ] In general, functionalize and modularize throughout. Remove as many if/else as possible; replace with dictionaries and more extensible behavior. 
