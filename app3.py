import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
trade_data1 = pd.read_csv('tab3data1.csv')

def plot_import_export_stacked_and_lines_by_country(country):
    trade_data_select = trade_data1[trade_data1['importer_name'] == country]

    # Stacked bar chart
    fig_stacked = go.Figure()
    fig_stacked.add_trace(go.Bar(
        x=trade_data_select['year'],
        y=trade_data_select['import_value'],
        name='Imports',
        marker_color='darkred'
    ))
    fig_stacked.add_trace(go.Bar(
        x=trade_data_select['year'],
        y=trade_data_select['export_value'],
        name='Exports',
        marker_color='lightyellow'
    ))
    fig_stacked.update_layout(
        title=f"Total Imports and Exports between the United States and {country} Over Time",
        xaxis=dict(title='Year'),
        yaxis=dict(title='Trade Value (in USD)'),
        barmode='stack'
    )

    # Line plot
    fig_lines = go.Figure()
    fig_lines.add_trace(go.Scatter(
        x=trade_data_select['year'],
        y=trade_data_select['import_value'],
        name='Imports',
        mode='lines+markers',
        line=dict(color='darkred', width=2)
    ))
    fig_lines.add_trace(go.Scatter(
        x=trade_data_select['year'],
        y=trade_data_select['export_value'],
        name='Exports',
        mode='lines+markers',
        line=dict(color='lightyellow', width=2),
        fill='tonexty',
        fillcolor='rgba(139,0,0,0.2)',
    ))
    fig_lines.update_layout(
        title=f"Imports and Exports Growth between the United States and {country} Over Time",
        xaxis=dict(
            title='Year',
            tickvals=[2018, 2019, 2020, 2021, 2022],
            ticktext=['2018', '2019', '2020', '2021', '2022']
        ),
        yaxis=dict(title='Trade Value (in USD)'),
    )

    return fig_stacked, fig_lines

def create_treemap_q(data, title, type): # Tree Map with Quantity (Not used in the app)
    color_scale = [
        [0, 'rgb(255, 215, 0)'],    # Gold (lower values)
        [0.2, 'rgb(255, 140, 0)'],  # Dark Orange
        [0.5, 'rgb(255, 69, 0)'],   # Orange Red
        [0.8, 'rgb(178, 34, 34)'],  # Firebrick
        [1, 'rgb(128, 0, 0)']       # Dark Red (higher values)
    ]
    fig = px.treemap(data, path=['Product Name'], values=type + '_quantity',  # Size by volume
                    title=title,
                    color=type + '_value', color_continuous_scale=color_scale,  # Color by trade value
                    hover_data={type + '_quantity': True, type + '_value': True})  # Show values on hover
    fig.update_traces(texttemplate='<b>%{label}</b>', textfont_size=14)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
        font=dict(color='white'),  # White font for dark theme
        margin=dict(t=50, l=25, r=25, b=25)
    )
    fig.update_layout(dragmode='zoom')  # Enable zoom feature
    fig.update_traces(root_color="darkred")  # Darker root color for better contrast

    return fig
    

def show_page():
    # Streamlit app layout
    st.sidebar.header("Select Options")

    country_list = trade_data1['importer_name'].unique().tolist()
    selected_country = st.sidebar.selectbox("Select a Country", country_list, index=country_list.index("China"))

    st.title(f"US - {selected_country} Trade Dashboard") 

    if selected_country:
        fig_stacked, fig_lines = plot_import_export_stacked_and_lines_by_country(selected_country)
        tree_map_data = pd.read_csv('tab3data2.csv')
        tree_map_data['Trade Deficit'] = tree_map_data['import_value'] - tree_map_data['export_value']
        tree_map_data_country = tree_map_data[tree_map_data['country'] == selected_country]

        # Layout with 2 columns on top and 1 row at the bottom
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_stacked, use_container_width=True)
        with col2:
            st.plotly_chart(fig_lines, use_container_width=True)

        # Imports/Exports button above treemap
        view_choice = st.radio("Select View:", ["Imports", "Exports"], horizontal=True)

        

        # Treemap selection based on Imports or Exports
        if view_choice == "Exports":
            tree_map_fig = create_treemap_q(tree_map_data_country, f"Treemap of Export with {selected_country} by HS Categories","export")
        else:
            tree_map_fig = create_treemap_q(tree_map_data_country, f"Treemap of Import with {selected_country} by HS Categories","import")
        # Full-width treemap below with button control above
        st.plotly_chart(tree_map_fig, use_container_width=True)

