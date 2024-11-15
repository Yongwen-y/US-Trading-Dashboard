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

def create_treemap_q(data, type): # Tree Map with Quantity (Not used in the app)
    data = data[data[type + '_value'] > 0]  # Filter out zero values
    data = data.sort_values(by=type+'_value', ascending=False).head(10)
    color_scale = [
        [0, 'rgb(255, 215, 0)'],    # Gold (lower values)
        [0.2, 'rgb(255, 140, 0)'],  # Dark Orange
        [0.5, 'rgb(255, 69, 0)'],   # Orange Red
        [0.8, 'rgb(178, 34, 34)'],  # Firebrick
        [1, 'rgb(128, 0, 0)']       # Dark Red (higher values)
    ]
    fig = px.treemap(data, path=['Product Name'], values= type + '_value',  # Size by volume
                    color=type + '_quantity', color_continuous_scale=color_scale,  # Color by trade value
                    hover_data={type + '_quantity': True, type + '_value': True})  # Show values on hover
    fig.update_traces(texttemplate='<b>%{label}</b>', textfont_size=14)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white'),  
        margin=dict(t=50, l=25, r=25, b=25), 
        height=600, width=600
    )
    fig.update_layout(dragmode='zoom')  # Enable zoom feature
    fig.update_traces(root_color="darkred")  # Darker root color for better contrast

    return fig
    

def show_page():
    # Streamlit app layout
    st.sidebar.header("Select Options")

    country_list = trade_data1['importer_name'].unique().tolist()
    selected_country = st.sidebar.selectbox("Select a Country", country_list, index=country_list.index("China"))
    view_choice = st.sidebar.radio("Select View:", ["Imports", "Exports"], horizontal=True)

    st.title(f"US - {selected_country} Trade Dashboard") 

    st.markdown(f"## test")
    fig_stacked, fig_lines = plot_import_export_stacked_and_lines_by_country(selected_country)
    tree_map_data_2022 = pd.read_csv('tab3data2.csv')
    tree_map_data_country_2022 = tree_map_data_2022[tree_map_data_2022['country'] == selected_country]
    tree_map_data_country_2022= tree_map_data_country_2022.sort_values(by='export_value', ascending=False).head(10)

    tree_map_data_2018 = pd.read_csv('tab3data3.csv')
    tree_map_data_country_2018 = tree_map_data_2018[tree_map_data_2018['country'] == selected_country]
    tree_map_data_country_2018 = tree_map_data_country_2018.sort_values(by='export_value', ascending=False).head(10)

    # Layout with 2 columns on top and 1 row at the bottom
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_stacked, use_container_width=True)
    with col2:
        st.plotly_chart(fig_lines, use_container_width=True)

    # Imports/Exports button above treemap
    
    st.markdown(f"## Product Composition Comparison from 2018 to 2022")

    col = st.columns([0.5,0.5], gap='small')

    with col[0]:
        if view_choice == "Exports":
            st.markdown(f"### Top 10 Exported Products in 2018")
            tree_map_fig2018 = create_treemap_q(tree_map_data_country_2018,"export")
        else:
            st.markdown(f"### Top 10 Imported Products in 2018")
            tree_map_fig2018 = create_treemap_q(tree_map_data_country_2018,"import")
        st.plotly_chart(tree_map_fig2018, use_container_width=True)

    with col[1]:
        # 2022
        if view_choice == "Exports":
            st.markdown(f"### Top 10 Exported Products in 2022")
            tree_map_fig2022 = create_treemap_q(tree_map_data_country_2022,"export")
        else:
            st.markdown(f"### Top 10 Exported Products in 2022")
            tree_map_fig2022 = create_treemap_q(tree_map_data_country_2022,"import")
        st.plotly_chart(tree_map_fig2022, use_container_width=True)








        