import pandas as pd
from pandas.api.types import CategoricalDtype
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html


## read data from URL into pandas

#url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=685000'
url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=6850'
trees = pd.read_json(url)


## change health to categorical, replace missing values with "Fair"

def clean_data(df):
    cat_type = CategoricalDtype(categories=["Poor", "Fair", "Good"], ordered=True)
    df['health'] = df['health'].astype(cat_type)
    df['health'] = df['health'].fillna('Fair')
    df['health'] = df['health'].cat.codes
    df['steward'] = df['steward'].fillna('None')

    return df

trees = clean_data(trees)

boros = list(trees['boroname'].unique())
boros.sort()

## Dash App

## display histograms using simple button selection

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='Tree Health NYC'),
    html.P('Examine health of trees in NYC boroughs with this application'),
    html.H2(children='Health by Borough'),
    html.P('Select a Borough: '),
    dcc.RadioItems(
        id='dropdown-a',
        options=[{'label': i, 'value': i} for i in boros],
        value='Bronx'
    ),
    html.Div(id='output-a'),
    html.H2('Health by Stewardship'),
    html.P("Select a stewardship level"),
    dcc.RadioItems(
        id='dropdown-b',
        options=[{'label': i, 'value': i} for i in trees['steward'].unique()],
        value='None'
    ),
    html.Div(id='output-b')
])


@app.callback(
    Output(component_id='output-a', component_property='children'),
    [Input(component_id='dropdown-a', component_property='value')]
)
def boro_graph(input_data):
    boro_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +
                '$select' +
                '&$where=boroname=\'{}\'' +
                '&$limit=685000').format(input_data).replace(' ', '%20')
    boro_trees = pd.read_json(boro_url)
    boro_trees = clean_data(boro_trees)

    return dcc.Graph(
        id='Health by Borough',
        figure={
            'data': [
                {'x': boro_trees['health'], 'type': 'histogram', 'name': 'Health by Borough'}
            ],
            'layout': {
                'title': "Health by Borough"
            }
        }
    )


@app.callback(
    Output(component_id='output-b', component_property='children'),
    [Input(component_id='dropdown-b', component_property='value')]
)
def steward_graph(input_data):
    steward_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +
                '$select' +
                '&$where=steward=\'{}\'' +
                '&$limit=685000').format(input_data).replace(' ', '%20')
    steward_trees = pd.read_json(steward_url)
    steward_trees = clean_data(steward_trees)


    df = trees[trees.steward == input_data]

    return dcc.Graph(
        id='Health by Steward',
        figure={
            'data': [
                {'x': steward_trees['health'], 'type': 'histogram', 'name': 'Health by Stewardship'}
            ],
            'layout': {
                'title': "Health by Stewardship"
            }
        }
    )


## running on http://127.0.0.1:8050/

if __name__ == '__main__':
    app.run_server(debug=False)
