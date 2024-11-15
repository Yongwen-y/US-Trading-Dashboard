import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load data
trade_data1 = pd.read_csv('tab3data1.csv')

def wrap_text(text, width=20):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= width:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return '<br>'.join(lines)

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
        xaxis=dict(title=''),
        yaxis=dict(title='',showgrid=False),
        barmode='stack',
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor='center',
            yanchor='top'
        ),
        height=500,
        margin=dict(t=0, l=0, r=0, b=0), 
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
        xaxis=dict(
            tickvals=[2018, 2019, 2020, 2021, 2022],
            ticktext=['2018', '2019', '2020', '2021', '2022']
        ),
        yaxis=dict(title='',showgrid=False),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.1,
            xanchor='center',
            yanchor='top'
        ),
        height=500,
        margin=dict(t=0, l=0, r=0, b=0),
    )

    return fig_stacked, fig_lines

def create_treemap_q(data, type): 
    data.sort_values(by=type+'_value', ascending=False, inplace=True)
    data = data[data[type + '_value'] > 0]  # Filter out zero values
    data.reset_index(drop=True, inplace=True)
    data = data.head(10)
    
    data[type + '_value'] = (data[type + '_value'] / 1e9)
    data[type + '_quantity'] = (data[type + '_quantity'] / 1e6).round(2)

    data['Product Name'] = data['Product Name'].apply(lambda x: wrap_text(x, 20))
    
    color_scale = [
        [0, 'rgb(255, 215, 0)'],    # Gold (lower values)
        [0.2, 'rgb(255, 140, 0)'],  # Dark Orange
        [0.5, 'rgb(255, 69, 0)'],   # Orange Red
        [0.8, 'rgb(178, 34, 34)'],  # Firebrick
        [1, 'rgb(128, 0, 0)']       # Dark Red (higher values)
    ]
    fig = px.treemap(data, path=['Product Name'], values= type + '_value',  # Size by volume
                    color=type + '_quantity', color_continuous_scale=color_scale,  # Color by trade value
                    hover_data={type + '_quantity': ':.4f', type + '_value': ':.4'})
    fig.update_traces(texttemplate='<b>%{label}</b>', textfont_size=20,
                      hovertemplate='<b>%{label}</b><br>Value: %{value:.4f} billion USD<br>Quantity: %{color:.4f} Millions Metric Tonnes')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  
        plot_bgcolor='rgba(0,0,0,0)',  
        font=dict(color='white'),  
        margin=dict(t=50, l=25, r=25, b=25), 
        height=500, width=550,
        dragmode='zoom', 
        coloraxis_colorbar=dict(
            title="Quantity",
            orientation="h",  
            x=0.5,  
            y=-0.2,  
            xanchor='center',
            yanchor='bottom',
        ),
    )
    fig.update_layout(dragmode='zoom', margin=dict(t=0, l=0, r=0, b=0),)  
    fig.update_traces(root_color="darkred")  

    return fig
    

def show_page():
    # Streamlit app layout
    st.sidebar.header("Select Options")

    country_list = trade_data1['importer_name'].unique().tolist()
    selected_country = st.sidebar.selectbox("Select a Country", country_list, index=country_list.index("China"))
    view_choice = st.sidebar.radio("Select View:", ["Imports", "Exports"], horizontal=True)

    st.markdown(f"<h1 style='text-align: center;'>US - {selected_country} Trade Dashboard</h1>", unsafe_allow_html=True)

    fig_stacked, fig_lines = plot_import_export_stacked_and_lines_by_country(selected_country)
    tree_map_data_2022 = pd.read_csv('tab3data2.csv')
    tree_map_data_country_2022 = tree_map_data_2022[tree_map_data_2022['country'] == selected_country]

    tree_map_data_2018 = pd.read_csv('tab3data3.csv')
    tree_map_data_country_2018 = tree_map_data_2018[tree_map_data_2018['country'] == selected_country]

    # Layout with 2 columns on top and 1 row at the bottom
    col = st.columns([0.5,0.5], gap='medium')

    with col[0]:
        st.markdown(f"#### Export/Import from 2018 to 2022")
        st.plotly_chart(fig_stacked, use_container_width=True)
    with col[1]:
        st.markdown(f"#### Trade Balance from 2018 to 2022")
        st.plotly_chart(fig_lines, use_container_width=True)
    
    st.markdown(f"## Product Composition Comparison from 2018 to 2022")
    col = st.columns([0.5,0.5], gap='medium')

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
            st.markdown(f"### Top 10 Imported Products in 2022")
            tree_map_fig2022 = create_treemap_q(tree_map_data_country_2022,"import")
        st.plotly_chart(tree_map_fig2022, use_container_width=True)

    st.markdown("<p style='font-size:20px; font-style:italic; text-align:center; margin-top:0;'>*Size represents Trade Value in Billion USD, Color represents Quantity in Millions Metric Tonnes</p>", unsafe_allow_html=True)








        