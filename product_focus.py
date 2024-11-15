import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import numpy as np
import plotly.graph_objects as go

### PRODUCT FOCUS ###

# "/Users/kevinnathanael/Desktop/Columbia MSBA/Columbia MSBA Fall Semester/Data Visualization/Final Project Data"

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

# #region RELEVANT FUNCTIONS
def dollar(value, rounding=None):
    if rounding is None:
        return f"${value:,.0f}"
    else:
        value = value / (10**rounding)
        return f"{value:,.0f} billions"    

def make_choropleth(input_df, input_id, input_column):
    bins = [0, 1e5, 1e6, 10e6, 50e6, 100e6, 500e6, 1e9, 10e9, 50e9, 100e9, np.inf]
    labels = ['< 100K', '100K - 1M', '1M - 10M', '10M - 50M', '50M - 100M', '100M - 500M', '500M - 1B', '1B - 10B', '10B - 50B', '50B - 100B', '> 100B']
    color = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026', '#67001f', '#49000d']
    
    if (input_df[input_column]<0).any(): #adjust the bins for Trade Balance, since scale is different
        bins = [-np.inf, -150e9, -50e9, -30e9,-10e9, -5e9, -2.5e9,0, 0.1e9,0.2e9, 0.5e9, 1e9, 10e9, 30e9, np.inf]
        labels = ['<-150B', '-150B-50B', '-50B-30B', '-30B-10B', '-10B-5B', '-5B-2.5B', '-2.5B-0', 
                  '0B-0.1B', '0.1B-0.2B', '0.2B-0.5B', '0.5B-1B', '1B-10B', '10B-30B', '>30B']
        color = ["#800026", "#bd0026", "#e31a1c", "#fc4e2a", "#fd8d3c", "#feb24c", "#fed976", #negative
                 "#eff3ff", "#bdd7e7", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594"] #positive

    # Assign each value to a bin
    input_df['binned_' + input_column] = pd.cut(input_df[input_column], bins=bins, labels=labels)

    # Ensure the order is maintained by sorting the DataFrame by the categorical column
    input_df = input_df.sort_values(by='binned_' + input_column)

    hover_data = {
        input_id: False,
        input_column: False,
        'binned_' + input_column: False,
        'value': True  # Include export_value in hover data
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
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
        width=650,
        geo=dict(
            showframe=False,
            showcoastlines=False,  # Hide coastlines
            projection_type='equirectangular',
            scope='world',  # Limit to the world, excluding Antarctica
            resolution=110,
            showland=True,
            landcolor='white',  # Adjust land color if needed
            showocean=False,  # Hide ocean
            lakecolor='rgba(0, 0, 0, 0)',  # Make lakes transparent
            bgcolor='rgba(0, 0, 0, 0)'  # Ensure full transparency
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
        showocean=False,  # Ensure ocean is not shown
        lataxis_range=[-60, 90]  # Limit latitude to exclude Antarctica
    )
    return choropleth
##################################

def show_page():
    ## read data file and data preprocessing 
    df_exp = pd.read_csv('exports_grouped.csv')
    df_imp = pd.read_csv('imports_grouped.csv')
    

    # FILTER OPTION
    st.sidebar.title("Filters")
    selected_year = st.sidebar.selectbox("Select Year", df_exp['year'].unique())
    selected_type = st.sidebar.radio("Select Data Type", ("Export", "Import", "Trade Balance"))
    selected_product = st.sidebar.selectbox("Select Product Type", sorted(df_exp['Product Type'].unique()), index=6)

    # FILTERING DATA BASED ON THE FILTER
    df_exp_filtered = df_exp[(df_exp['year'] == selected_year) & (df_exp['Product Type'] == selected_product)]
    df_exp_filtered = df_exp_filtered.groupby(['importer_name', 'year', 'Product Type']).agg({'value': 'sum'}).reset_index()
    df_exp_filtered.rename(columns={'importer_name': 'partner'}, inplace=True)

    df_imp_filtered = df_imp[(df_imp['year'] == selected_year) & (df_imp['Product Type'] == selected_product)]
    df_imp_filtered = df_imp_filtered.groupby(['exporter_name', 'year', 'Product Type']).agg({'value': 'sum'}).reset_index()
    df_imp_filtered.rename(columns={'exporter_name': 'partner'}, inplace=True)

    df_balance = df_exp_filtered.merge(df_imp_filtered, on='partner', suffixes=('_export', '_import')).drop(columns=['year_export', 'Product Type_export'])
    df_balance['value'] = df_balance['value_export'] - df_balance['value_import']
    df_balance.rename(columns={'year_import' : 'year', 'Product Type_import': 'Product Type'}, inplace=True)

    if selected_type == "Export":
        data = df_exp_filtered
    elif selected_type == "Import":
        data = df_imp_filtered
    else:
        data = df_balance
    col = st.columns([0.75, 0.25], gap='small')

    with col[0]:
        #Chloropleth
        choropleth = make_choropleth(data, 'partner','value')
        st.plotly_chart(choropleth, use_container_width=True)

    with col[1]:
        st.markdown(f"#### Top 10 {selected_type} Partners for {selected_product}")
        top_trade_partners = data.groupby('partner').agg({'value': 'sum'}).sort_values(by='value', ascending=False).head(10)
        top_trade_partners['formatted_value'] = top_trade_partners['value'] / 1e8

        st.dataframe(top_trade_partners,
                    column_order=("partner", "formatted_value"),
                    hide_index=True,
                    width=None,
                    use_container_width=True,
                    column_config={
                    "partner": st.column_config.TextColumn(
                        "Trade Partner",  
                    ),
                    "formatted_value": st.column_config.ProgressColumn(
                        "Trade Value (in hundreds millions)",
                        format="%.2f",
                        min_value=0,
                        max_value=max(top_trade_partners['value']) / 1e8,
                        )}
                    )

    ### SECOND ROW
    col = st.columns([0.35, 0.4, 0.25], gap='small')

    # BAR CHART
    with col[0]:
        st.markdown(f"### Trade Summary for {selected_product}")
        total_export_product = df_exp_filtered['value'].sum()
        total_import_product = df_imp_filtered['value'].sum()
        summary = {
            "Category": ["Export", "Import", "Trade Balance"],
            "Value": [total_export_product/1e9, -total_import_product/1e9, (total_export_product-total_import_product)/1e9]
        }
        df = pd.DataFrame(summary)
        color_scale = ['darkred', '#FF7F00', 'yellow', '#FFFFE0', '#FFFFFF']

        fig = px.bar(df, x="Category", y="Value", text="Value",
                    color="Value", color_continuous_scale=color_scale)

        fig.update_layout(
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),  # Hide y-axis and title
            xaxis=dict(showgrid=False, zeroline=False, title='', tickfont=dict(size=18), title_standoff=20),
            plot_bgcolor='rgba(0,0,0,0)',  
            paper_bgcolor='rgba(0,0,0,0)',  
            bargap=0.05,  
            coloraxis_showscale=False,
            margin=dict(t=0, b=10, l=10, r=10)
        )

        fig.update_traces(
            texttemplate='%{text:.1f} B USD', textposition='inside',
            insidetextanchor='middle',  
            marker_line_width=0,  
            textfont=dict(size=18)  
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col[1]:
        st.markdown(f"### {selected_type} for {selected_product} over the years")

        exp_data = df_exp[(df_exp['Product Type'] == selected_product)].groupby('year').agg({'value': 'sum'}).reset_index()
        imp_data = df_imp[(df_imp['Product Type'] == selected_product)].groupby('year').agg({'value': 'sum'}).reset_index()

        
        fig_line = go.Figure()

        
        fig_line.add_trace(go.Scatter(
            x=imp_data['year'], y=imp_data['value'],
            mode='lines+markers',
            name='Import',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='<br><b>Import Value</b>: %{y}<extra></extra>'
        ))

        
        fig_line.add_trace(go.Scatter(
            x=exp_data['year'], y=exp_data['value'],
            mode='lines+markers',
            name='Export',
            line=dict(color='white', width=3),
            marker=dict(size=8)
        ))

        
        fig_line.update_layout(
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title='', tickfont=dict(size=18)),  # Hide y-axis grid and title
            xaxis=dict(showgrid=False, zeroline=False, title='', tickfont=dict(size=18), title_standoff=20),
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper
            margin=dict(t=10, b=0, l=10, r=10),
            legend=dict(orientation='h',font=dict(size=14), yanchor='bottom', y=-0.25, xanchor='center', x=0.5)  # Adjust legend font size and position  # Adjust legend font size
        )

        
        fig_line.add_trace(go.Scatter(
            x=exp_data['year'].tolist() + imp_data['year'].tolist()[::-1],
            y=exp_data['value'].tolist() + imp_data['value'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)' if (exp_data['value'] - imp_data['value']).sum() < 0 else 'rgba(255, 255, 255, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo='skip',
            showlegend=False
        ))

        
        st.plotly_chart(fig_line, use_container_width=True)

        with col[2]:
            links = pd.read_csv('image_link.csv')
            links = links[links['Group'] == selected_product]
   
            with st.expander(f"#### Example Products",expanded=True):
                cols = st.columns(2)
                count = 0
                for index, row in links.iterrows():
                    col_index = index % 2  # Determine which column to use
                    if count >= 4:
                        break
                    with cols[col_index]:
                        st.image(row['url'], caption=row['Sampled Products'])
                    count +=1