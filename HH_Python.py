from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

df = pd.read_csv('https://raw.githubusercontent.com/Burmand/Dashboard_python_hh/main/HH_Dataset_python.csv', sep = ";")

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exeptions = True    

df['published_date'] = pd.to_datetime(df['published_at'])
df['published_month'] = pd.to_datetime(df['published_at']).dt.strftime('%Y-%m')
df['published_year'] = pd.to_datetime(df['published_at']).dt.strftime('%Y')

df['salary'] = df[['salary_from','salary_to']].mean(axis=1)

df['position'] = None
df['position'] = np.where(df['name'].str.contains('Middle|middle') & ~df['name'].str.contains('Senior|senior') & ~df['name'].str.contains('Junior|junior'), 'Middle', df['position'])
df['position'] = np.where(df['name'].str.contains('Junior|junior') & ~df['name'].str.contains('Middle|middle'), 'Junior', df['position'])
df['position'] = np.where(df['name'].str.contains('Senior|senior') & ~df['name'].str.contains('Middle|middle'), 'Senior', df['position'])

SIDESTYLE = {
    'width': '20%',
    'height': '100%',
    'background-color': '#f8f9fa',
    'padding': '20px',
    'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'position': 'fixed'
}

CONTSTYLE = {
    'width': '80%',
    'height': '100%',
    'padding-top': '20px',
    'margin-left': '20%',
}


app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([    
        html.H2("Разделы", style={'color': '#007bff'}),
            html.Hr(style={'color': 'white'}),
            dbc.Nav([
                    dbc.NavLink("Города", href="/page1", active="exact"),
                    dbc.NavLink("Работодатели", href="/page2", active="exact"),
                ],
                vertical=True,pills=True),
        ],
        style=SIDESTYLE,
    ),
    html.Div(id="page-content", children=[], style=CONTSTYLE)
])


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)


def pagecontent(pathname):
    if pathname == "/page1":
        return [
        html.Div(
            [
                html.H5('Города', style={'margin-left':'15px'}),
                dcc.Dropdown(
                    id = 'dropdown-city',
                    options = [{'label': i, 'value': i} for i in df['area_name'].unique()],
                    value = ['Москва','Санкт-Петербург', 'Новосибирск', 'Екатеринбург',
                             'Нижний Новгород', 'Самара','Краснодар','Минск','Казань', 'Ростов-на-Дону'],
                    multi = True
                )
            ]),
        html.Div(
            dcc.Graph(id = 'vacancy-dynamics'),
        ),
        html.Div(
            dcc.Graph(id = 'vacancies-by-city')
        ),
        html.Div(
            dcc.Graph(id = 'salary-by-city')
        ),
        html.Div(
            dcc.Graph(id = 'employer-by-city')
        ),
html.Div(
            [
                html.H5("Настройки", style={"margin-bottom": "10px"}),
                dbc.Row([
                        dbc.Col(
                            [
                                dbc.Label("Показатель"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Медианная зарплата", "value": "median"},
                                        {"label": "Средняя зарплата", "value": "average"},
                                    ],
                                    value="median",
                                    id="radioitems-parameter",
                                    style={"font-size": "14px"}
                                ),
                            ],
                            width=2,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Шкала"),
                                dbc.Switch(
                                    value=False,
                                    id="switch-scale",
                                ),
                            ],
                            width=1,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Минимальное количество вакансий", style={'margin-left': '25px'}),
                                dcc.Slider(
                                    min=1,
                                    max=10,
                                    step=1,
                                    value=3,
                                    marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True},
                                    id="slider-min-count"
                                )
                            ],
                            width=4,
                        ),
                    ]),
            ],
            style={"background-color": "#f8f8f8", "padding": "20px", "border": "1px solid #ddd", "border-radius": "5px", "margin": "10px"},
        ),
        html.Div(
            dcc.Graph(id = 'salary-by-position'),
            style={'display': 'flex', 'justify-content': 'center'}  
        )]
    elif pathname == "/page2":
        return [
        html.Div([
            html.Label('Период:'),
            html.Div([
                dcc.DatePickerRange(
                    id='datepicker',
                    display_format='DD/MM/YYYY',
                    first_day_of_week=1,
                    start_date=pd.to_datetime('2020-06-05').tz_localize('UTC'),
                    end_date=pd.to_datetime('2021-06-05').tz_localize('UTC'))],
                    style={'margin-top': '5px'})],
                    style={'width': '100%', 'margin-bottom': '20px', 'margin-left': '25px'}),
                html.Div([
                    html.Label('Минимальное количество вакансий:', style={'margin-left': '25px'}),
                    dcc.Slider(
                            min=1,
                            max=10,
                            step=1,
                            value=5,
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": True},
                            id='slider'
                            )], style= {'width': '50%', 'margin-bottom': '20px'}),
                    html.Div([dcc.Graph(id = 'salary-by-employer')])]
            

@callback(
    Output('vacancy-dynamics', 'figure'),
    [Input('dropdown-city', 'value')]
)
def update_scatter(city):
    df_in_cities = df[df['area_name'].isin(city)]
    jobs_postings_per_month = df_in_cities.groupby(['published_month', 'published_year'])['id'].count().reset_index()
    jobs_postings_per_month = jobs_postings_per_month.sort_values(by=['published_year', 'published_month'])
    
    figure = go.Figure(data=go.Scatter(
        x=jobs_postings_per_month['published_month'],
        y=jobs_postings_per_month['id'],
        mode='lines+markers',
        line=dict(color='blue')
    ))

    figure.update_layout(
        title = 'Динамика вакансий',
        xaxis=dict(title='Месяц'),
        yaxis=dict(title='Количество вакансий')
    )
    return figure   

@callback(
    Output('vacancies-by-city', 'figure'),
    [Input('dropdown-city', 'value')]
)
def update_pie_chart(city):
    vacancies_by_city = df['area_name'].value_counts()
    vacancies_by_city = vacancies_by_city[vacancies_by_city.index.isin(city)]
    
    figure = go.Figure(data=go.Pie(labels=vacancies_by_city.index,
                                   values=vacancies_by_city.values))
    figure.update_layout(title = 'Количество ваканский по городам',
                         width = 700,
                         height = 700)
    
    return figure

@callback(
    Output('salary-by-city', 'figure'),
    [Input('dropdown-city', 'value')]
)
def update_barchart_city(city):
    avg_salary_by_area = df.groupby('area_name')['salary'].mean()
    top_cities = avg_salary_by_area.sort_values(ascending = False)
    top_cities = top_cities[top_cities.index.isin(city)]

    figure = go.Figure(data = [go.Bar(x = top_cities.index,
                                      y = top_cities.values,
                                      marker = {'color': top_cities.values})])
    figure.update_layout(title = 'Средняя зарплата по городу',
                         xaxis_title = 'Город',
                         yaxis_title = 'Средняя зарплата')
    return figure

@callback(
     Output('employer-by-city','figure'),
     [Input('dropdown-city', 'value')]
)
def update_barchart_employer_by_city(city):
    top_employer_by_city = df.groupby(['area_name', 'employer_name'])['id'].count().reset_index()
    top_employer_by_city = top_employer_by_city.loc[top_employer_by_city.groupby('area_name')['id'].idxmax()]
    top_employer_by_city = top_employer_by_city[top_employer_by_city['area_name'].isin(city)]
    top_employer_by_city = top_employer_by_city.sort_values(by='id', ascending=False)

    figure = go.Figure(data = [go.Bar(x = top_employer_by_city['area_name'],
                                      y = top_employer_by_city['id'],
                                      text = top_employer_by_city['employer_name'],
                                      marker = {'color': top_employer_by_city['id']})])
    
    figure.update_layout(title='Работодатели, которые чаще всего размещают вакансии в городе',
                         xaxis_title='Город',
                         yaxis_title='Количество вакансий')
    return figure

@callback(
    Output('salary-by-position', 'figure'),
    [Input('dropdown-city', 'value'),
     Input('switch-scale', 'value'),
     Input('radioitems-parameter', 'value'),
     Input('slider-min-count', 'value')]
)
def update_sunburst_salary_by_position(city, switch_value, radiobutton_parameter, slider_min_count):
    salary_parameter = ''
    salary_parameter_bar = ''

    filtered_data = df.dropna(subset=['position'])
    filtered_data = filtered_data[filtered_data['area_name'].isin(city)]
    count = filtered_data.groupby(['position', 'area_name']).size().reset_index(name='count')
    count = count[count['count']>=slider_min_count]

    if radiobutton_parameter == 'average':
        salary_parameter,salary_parameter_bar = 'средней', 'Средняя зарплата'
        salary_info = round(filtered_data.groupby(['position', 'area_name'])['salary'].mean().reset_index())
        count = count.merge(salary_info, on=['position', 'area_name'], how='left')
        position_info = round(count.groupby('position')['salary'].mean().reset_index())  
    else:
        salary_parameter, salary_parameter_bar = 'медианной', 'Медианная зарплата'
        salary_info = filtered_data.groupby(['position', 'area_name'])['salary'].median().reset_index()
        count = count.merge(salary_info, on=['position', 'area_name'], how='left')
        position_info = count.groupby('position')['salary'].median().reset_index()

    count = count.merge(position_info, on='position')

    count['area_name'] = count['area_name'] + '\n(₽' + count['salary_x'].astype(str) + ')'
    count['position'] = count['position'] + '\n(₽' + count['salary_y'].astype(str) + ')'

    if switch_value:
        figure = px.sunburst(count, path=['position', 'area_name'], values='count', color = 'salary_x', color_continuous_scale='blues')
    else:
        figure = px.sunburst(count, path=['position', 'area_name'], values='count')

    figure.update_layout(title={'text': f'Количество ваканский по должности и городу с указанием {salary_parameter} зарплаты', 'font': {'size': 16}},
                        width=800,
                        height=800,
                        font = {'size': 16},
                        coloraxis_colorbar_title_text  = salary_parameter_bar,
                        coloraxis_colorbar_title_font = {'size':14},
                        coloraxis_colorbar_title_side = 'right')

    return figure

@callback(
    Output('salary-by-employer', 'figure'),
    [Input('datepicker','start_date'),
     Input('datepicker','end_date'),
     Input('slider','value')]
)
def update_barchart_employer(start_date, end_date, count_number):
    df_within_date = df[(df['published_date']>start_date) & (df['published_date']<end_date)]
    avg_salary = df_within_date.groupby('employer_name')['salary'].agg(['mean','count'])
    avg_salary = avg_salary[avg_salary['count'] >= count_number]
    top_employers = avg_salary.sort_values('mean', ascending = False)

    figure = go.Figure(data=[go.Bar(x=top_employers.index,
                                    y=top_employers['mean'],
                                    marker={'color':top_employers['mean']})])
    
    figure.update_layout(title = 'Средняя зарплата по работодателям',
                         xaxis_title = 'Работодатель',
                         yaxis_title = 'Средняя зарплата')
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)