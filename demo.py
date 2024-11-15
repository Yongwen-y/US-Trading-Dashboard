import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import numpy as np
import plotly.graph_objects as go

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
        
</style>
""", unsafe_allow_html=True)

#################### RELEVANT FUNCTIONS
def dollar(value, rounding=None):
    if rounding is None:
        return f"${value:,.0f}"
    else:
        value = value / (10**rounding)
        return f"{value:,.0f} billions"
    
def make_choropleth(input_df, input_id, input_column):
    bins = [0, 500e6, 1e9, 3e9, 8e9, 18e9, 36e9, 71e9, 200e9, np.inf]
    labels = ['0-500M', '500M-1B', '1B-3B', '3B-8B', '8B-18B', '18B-36B', '36B-71B', '71B-200B', '> 200B']
    color = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
    if (input_df[input_column]<0).any(): #adjust the bins for Trade Balance, since scale is different
        bins = [-np.inf, -200e9, -100e9, -30e9,-10e9, 0, 0.1e9,0.2e9, 0.5e9, 1e9, 10e9, 30e9, np.inf]
        labels = ['<-200B', '-200B-100B', '-100B-30B', '-30B-10B', '-10B-0', '0-0.1B', '0.1B-0.2B', '0.2B-0.5B', '0.5B-1B', '1B-10B', '10B-30B', '>30B']
        color = ["#800026", "#bd0026","#e31a1c","#fc4e2a", "#feb24c", #negative
                 "#d0e1f2", "#a6bddb", "#74a9cf", "#2b8cbe", "#0570b0", "#045a8d", "#023858"] #positive
    # Assign each value to a bin
    input_df['binned_' + input_column] = pd.cut(input_df[input_column], bins=bins, labels=labels)

    # Ensure the order is maintained by sorting the DataFrame by the categorical column
    input_df = input_df.sort_values(by='binned_' + input_column)

    hover_data = {
        input_id: False,
        input_column: False,
        'binned_' + input_column: False,
        'value_export': True  
    }  

    choropleth = px.choropleth(
        input_df,
        locations=input_id,
        color='binned_' + input_column,
        locationmode="country names", 
        category_orders={'binned_' + input_column: labels},
        color_discrete_sequence=color,
        labels={input_column: input_column},
        hover_name=input_id,
        hover_data = hover_data
    )

    choropleth.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' +
                      'Value: %{customdata[1]:,.0f} USD<br>' +
                      'Category: %{customdata[2]}<extra></extra>'
    )
    choropleth.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(0, 0, 0, 0)',  
        paper_bgcolor='rgba(0, 0, 0, 0)',  
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        width=680,
        geo=dict(
            showframe=False,
            showcoastlines=False,  
            projection_type='equirectangular',
            scope='world',  
            resolution=110,
            showland=True,
            landcolor='white',  
            showocean=False,  
            lakecolor='rgba(0, 0, 0, 0)', 
            bgcolor='rgba(0, 0, 0, 0)' 
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0,
            xanchor="center",
            x=0.5
        ),
    )
    choropleth.update_geos(
        visible=False,
        showcountries=True,
        countrycolor="Black",
        coastlinecolor="Black",
        showland=True,
        landcolor="white",
        showocean=False,  
        lataxis_range=[-60, 90] 
    )
    return choropleth

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
##################################

def show_page():
    ## read data file and data preprocessing 
    df_exp = pd.read_csv('exports_grouped.csv')
    df_imp = pd.read_csv('imports_grouped.csv')

    export_total = df_exp.groupby(['year', 'importer_name']).agg({'value': 'sum', 'Continent': 'first'}).reset_index()
    import_total = df_imp.groupby(['year', 'exporter_name']).agg({'value': 'sum'}).reset_index()

    trade_data = pd.merge(export_total, import_total, left_on=['year', 'importer_name'], right_on=['year', 'exporter_name'], suffixes=('_export', '_import'))
    trade_data = trade_data.assign(partner=trade_data['importer_name']).drop(columns=['importer_name', 'exporter_name'])
    trade_data['value_trade balance'] = trade_data['value_export'] - trade_data['value_import']

    #filters in the side bar
    st.sidebar.title("Filters")
    selected_year = st.sidebar.selectbox("Select Year", trade_data['year'].unique())
    selected_type = st.sidebar.radio("Select Data Type", ("Export", "Import", "Trade Balance"))
    value_column = 'value_' + selected_type.lower()

    filtered_data = trade_data[trade_data['year'] == selected_year]
    df_exp_filtered = df_exp[df_exp['year'] == selected_year]
    df_imp_filtered = df_imp[df_imp['year'] == selected_year]

    #### DATA VISUALIZATION
    # FIRST ROW
    col = st.columns([0.75, 0.25], gap='small')

    with col[0]:
        #Chloropleth
        choropleth = make_choropleth(filtered_data, 'partner',value_column)
        st.plotly_chart(choropleth, use_container_width=True)

    with col[1]:
        if selected_type != "Trade Balance":
            st.markdown(f"### Top 10 {selected_type} Partners")
            top_trade_partners = filtered_data.groupby('partner').agg({value_column: 'sum', 'Continent': 'first'}).sort_values(by=value_column, ascending=False).head(10)
        else: 
            st.markdown(f"### Countries With the  Biggest Trade Deficit with US")
            top_trade_partners = filtered_data.groupby('partner').agg({value_column: 'sum', 'Continent': 'first'}).sort_values(by=value_column, ascending=True)
            top_trade_partners[value_column] = top_trade_partners[value_column] * -1
        top_trade_partners['formatted_value'] = top_trade_partners[value_column] / 1e9

        st.dataframe(top_trade_partners,
                    column_order=("partner", "formatted_value"),
                    hide_index=True,
                    width=None,
                    column_config={
                    "partner": st.column_config.TextColumn(
                        "Trade Partner",  
                    ),
                    "formatted_value": st.column_config.ProgressColumn(
                        "Trade Value (in billions)",
                        format="%.2f",
                        min_value=0,
                        max_value= max(top_trade_partners[value_column]) / 1e9,
                        )}
                    )
    
    # SECOND ROW
    col = st.columns([0.3, 0.5, 0.2], gap='medium')
    with col[0]:
        data = {
            "Category": ["Export", "Import", "Trade Balance"],
            "Value": [filtered_data['value_export'].sum()/1e12, -filtered_data['value_import'].sum()/1e12, filtered_data['value_trade balance'].sum()/1e12]
        }
        df = pd.DataFrame(data)
        color_scale = ['darkred', '#FF7F00', 'yellow', '#FFFFE0', '#FFFFFF']

        fig = px.bar(df, x="Category", y="Value", text="Value",
                    color="Value", color_continuous_scale=color_scale)

        fig.update_layout(
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),  
            xaxis=dict(showgrid=False, zeroline=False, title='', tickfont=dict(size=18), title_standoff=20),
            plot_bgcolor='rgba(0,0,0,0)',  
            paper_bgcolor='rgba(0,0,0,0)', 
            bargap=0.05,  
            coloraxis_showscale=False 
        )

        fig.update_traces(
            texttemplate='%{text:.2} T USD', textposition='inside',
            insidetextanchor='middle',  
            marker_line_width=0,  
            textfont=dict(size=18)  
        )
        st.plotly_chart(fig, use_container_width=True)

    with col[1]:
        top_products_exp = df_exp_filtered.groupby('Product Type').agg({'value': 'sum'}).reset_index()
        top_products_imp = df_imp_filtered.groupby('Product Type').agg({'value': 'sum'}).reset_index()
        products_def = (top_products_imp.set_index('Product Type') - top_products_exp.set_index('Product Type')).sort_values(by='value', ascending=False).reset_index()

        if selected_type == "Export":
            st.markdown(f"### Top {selected_type}ed Products")
            top_products = top_products_exp
        elif selected_type == "Import":
            st.markdown(f"### Top {selected_type}ed Products")
            top_products = top_products_imp
        else: 
            st.markdown(f"### Products With the  Biggest Trade Deficit")
            top_products = products_def  
        top_products['wrapped_label'] = top_products['Product Type'].apply(wrap_text)
        top_products['formatted_value'] = top_products['value']/1e9

        fig_treemap = px.treemap(
            top_products,
            path=['wrapped_label'],
            values='formatted_value',
            color='formatted_value',
            color_continuous_scale=['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
        )
        fig_treemap.update_traces(
            textinfo="label+percent entry",
            textfont=dict(size=15),
            hovertemplate='<b>%{label}</b><br>Value: %{value:.1f} billion USD',
            texttemplate='%{label}<br>%{percentEntry:.2%}',
            marker=dict(line=dict(width=0)),
        )

        fig_treemap.update_layout(
            coloraxis_colorbar=dict(title="$ Billion USD", orientation='h', yanchor='bottom',y=-0.2, xanchor='center', x=0.5),
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            height = 400,
            width = 550,
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

    with col[2]:
        st.write(f"### Key Insights")
        st.write(f'1. The US has a long-running overall trade deficity')
        st.write(f'2. Largest Importing Partner: China')
        st.write(f'3. Largest Exporting Partner: Mexico & Canada')
        st.write('\n\n')
        st.write('\n\n')
        st.write('\n\n')
        with st.expander(f'# About:', expanded=False):
                st.write(f'''
                    - Source: [OEC](https://oec.world/en/resources/bulk-download/international)
                    - :orange[**Data Displayed**]: Displaying data for {selected_type} value of USA in {selected_year}
                    '''
                    
                    )
                     