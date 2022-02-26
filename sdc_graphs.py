import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from styling import datatable_styling

aligners_csv = pd.read_csv('aligner.csv')
year_min = aligners_csv['Year'].min()
year_max = aligners_csv['Year'].max()
avg_price_aligners = aligners_csv.groupby('US_State')['Aligners'].sum().reset_index()
map_figure = px.choropleth(avg_price_aligners,
                           locations='US_State',
                           locationmode='USA-states',
                           color='US_State',
                           scope='usa',
                           color_continuous_scale='blues')



app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    html.H1("sd Sales"),
    dcc.RangeSlider(
        id='year_slider',
        min=year_min,
        max=year_max,
        value=[year_min, year_max],
        marks={i: str(i) for i in range(year_min, year_max + 1)},
        # marks={i :{'label' : str(i), 'style':{'color':'purples'}} for i in range(year_min, year_max + 1)},
    ),
    dbc.Row([
        dcc.Graph(id='bar_plot'),
        dcc.Graph(id='map-graph', figure=map_figure),
    ]),
    html.Div(id='sample_div'),
    dash_table.DataTable(id='price_info',
                         columns=[{'name': col, 'id': col} for col in aligners_csv.columns],
                         data=aligners_csv.to_dict('records'),
                         style_cell_conditional= datatable_styling('Year','US_State','Aligners'),
                         # style_cell_conditional=[
                         #    {
                         #        'if': {'column_id': c},
                         #        'textAlign': 'center',
                         #        'width': '30%',
                         #    } for c in ['Year', 'US_State', 'Aligners']
                         # ],
                         style_as_list_view=True,
                         )
])


@app.callback(
    Output('map-graph', 'figure'),
    Input('year_slider', 'value')
)
def updated_rangeslider(input_year_slider):
    filter_aligners = aligners_csv[(aligners_csv['Year'] >= input_year_slider[0]) &
                                         (aligners_csv['Year'] <= input_year_slider[1])]

    avg_price_aligners = filter_aligners.groupby('US_State')['Aligners'].sum().reset_index()
    map_figure = px.choropleth(avg_price_aligners,
                               locations='US_State',
                               locationmode='USA-states',
                               color='Aligners',
                               scope='usa',
                               color_continuous_scale='blues')
    return map_figure


@app.callback(
    Output('price_info', 'data'),
    Output('bar_plot', 'figure'),
    Input('map-graph', 'clickData'),  # Input component property is click data.
    Input('year_slider', 'value')

)
def update_data_table_when_clicked_on_map(click_data, input_year_slider):
    if click_data is None:
        return [], bar_fig([], [])
    us_state = click_data['points'][0]['location']
    records = aligners_csv[(aligners_csv['US_State'] == us_state) &
                              (aligners_csv['Year'] >= input_year_slider[0]) &
                              (aligners_csv['Year'] <= input_year_slider[1])
                              ]
    records_to_dict = records.to_dict('records')
    avg_price_aligners_state = aligners_csv[aligners_csv['US_State'] == us_state].reset_index()
    get_res_value_year = avg_price_aligners_state[(avg_price_aligners_state['Year'] >= input_year_slider[0]) &
                                                     (avg_price_aligners_state['Year'] <= input_year_slider[1])]
    get_years = list(get_res_value_year['Year'])
    res_price_list = list(get_res_value_year['Aligners'])
    bar_figure = bar_fig(y_cordinate=res_price_list, x_cordinate=get_years, state=us_state)
    return records_to_dict, bar_figure


def bar_fig(x_cordinate=None, y_cordinate=None, state="."):
    if y_cordinate is None:
        y_cordinate = []
    bar_figure = go.Figure(
        data=[go.Bar(y=y_cordinate, x=x_cordinate)],
        layout_title_text=f"Bar Char for the state {state}"
    )
    return bar_figure


if __name__ == '__main__':
    app.run_server(debug=True)
