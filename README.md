# USA-Trade-Dashboard
Dashboard that outlines US Export and Import data from 2018-2022

App URL: https://usa-trade-dashboard-plot-twist-group.streamlit.app

Code Structure Outline: 
- Homepage.py : Run this first. This script is responsible for navigating between the 3 tabs on the dashboard
- demo.py :
    - Script for Trade Overview Tab.
    - This tab contains import/export data between US and the rest of the world
- product_focus.py:
    - Script for Product Focus Tab.
    - In this tab, user can select a specific product category and see the trade relationship data for US for the selected product category.
- app3.py
    - Script for Country Focus Tab
    - In this tab user, user can select a specific country and see the specific trade relationship that the US has with the selected country.
 
Data:

There are 5 CSV files that contain the required data to run this dashboard. 
All data were originially from https://oec.world/en/resources/bulk-download/international
Each csv file were a cleaned up and processed version from the raw data found in the url above.

- exports_grouped.csv :
    - contains exports data with all countries (importer) from 2018 to 2022, grouped by HS2 level product category
    - Columns: year,importer_name,hs2,value,quantity,hs_revision,Continent,Product Type
- import_grouped.csv :
    - Contains import data with all countries (exporter) from 2018 to 2022, grouped by HS2 level product category
    - Columns: year,exporter_name,hs2,value,quantity,hs_revision,Continent,Product Type
- tab3data1.csv : 
    - Shows total Export and Import value for all countries from 2018 to 2022
    - Columns: year,importer_name, export_value, exporter_name,import_value
    - Explanation for columns: importer_name is country that US export to. similarly, exporter_name is country that US import from. 
- tab3data2.csv :
    - Shows Export and Import value for all countries in 2022, along with the product description
    - Column: year,country,hs2,export_value,export_quantity,import_value,import_quantity,Product Name
- tab3data3.csv :
    - Shows Export and Import value for all countries in 2018, along with the product description
    - Column: year,country,hs2,export_value,export_quantity,import_value,import_quantity,Product Name
    
