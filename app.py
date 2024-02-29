from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import pandas as pd

# 實單交易資料處理
model_score = pd.read_parquet('data/模型指標五爪圖.parquet')
feature_importance = pd.read_parquet('data/特徵重要度.parquet')
backtest_data = pd.read_parquet('data/投組回測資料.parquet')
equity = pd.read_parquet('data/實單.parquet')
cumsum_ret_fig = px.line(backtest_data, x="trading_datetime", y="ret_portfolio_cumsum", color = 'n_stock', title = '累積報酬率折線圖', height=800, hover_data = ['long_stock', 'short_stock', 'portfolio_max_drawdown', 'ret_portfolio_dd'])
feature_importance['Importances'] = feature_importance.groupby('model_id')['Importances'].apply(lambda x: x/x.sum())


def showClickData_init():
    if True:
        select_date = backtest_data['trading_datetime'].astype('string').max()
        
        filterData = backtest_data[(backtest_data['trading_datetime'].astype('string') == select_date) & (backtest_data['n_stock'].astype('int') == int(1 * 2))]
        
        renameColname = {'trading_datetime' : '交易日期', 'ret_portfolio_cumsum' : '策略累積收益率', 'ret_portfolio' : '當日收益率', 
                 'ret_portfolio_dd' : '當日回撤', 'portfolio_max_drawdown': '策略最大回撤', 'long_stock' : '當日做多股票', 
                 'short_stock' : '當日做空股票', 
                 'long_short_corr' : '策略多空部位收益率相關性', 'ret_portfolio_winRate' : '策略勝率', 
                 'ret_portfolio_annualRet' : '策略年化收益率', 'VaR_5%_oneDay' : '策略5%VaR(天)'}
        showColumns = ['trading_datetime', 'ret_portfolio_cumsum', 'ret_portfolio', 'ret_portfolio_dd', 'long_stock', 'short_stock', 
                       'long_short_corr', 'ret_portfolio_winRate', 'ret_portfolio_annualRet', 'portfolio_max_drawdown', 'VaR_5%_oneDay']
        filterData['trading_datetime'] = filterData['trading_datetime'].astype('string')
        filterData = filterData[showColumns].rename(columns = renameColname).reset_index(drop = True).transpose().reset_index()
        
        filterData.columns = ['欄位', '數值']
        jsonData = filterData.to_dict('records')
        columns = [{"name" : i, 'id' : i} for i in filterData.columns]
        dataTable = dash_table.DataTable(jsonData, columns = columns, 
                                         style_data = {'color' : 'black', 'font_size' : '18px', 'textAlign' : 'left'}, 
                                         style_header = {'font_weight' : 'bold', 'color' : 'black', 'font_size' : '18px'})
        return(dataTable)


initTable = showClickData_init()

indicator_group_test = html.Div([
    html.Div([
        html.Div(['指標'], style = {'padding' : '3px', 'font-size' : '18px'}), 
        html.Div([dcc.Dropdown(
            model_score['score_indicator'].unique(),
            model_score['score_indicator'].unique().tolist()[0],
            id='model-score-test_indicator-dropdown'
        )], style = {'width' : '300px', 'padding' : '2px'})
    ], style = {'width' : '100vw', 'display': 'flex', 'align-items' : 'center', 'padding' : '4px'}),
    html.Div([
        html.Div(['分組數'], style = {'padding' : '3px', 'font-size' : '18px'}), 
        html.Div([dcc.Slider(
            model_score['nGroup'].min(), model_score['nGroup'].max(), value=model_score['nGroup'].min(),
            marks={str(model_score): str(model_score) for n_group in model_score['nGroup'].unique()},
            step = 5,
            id='ngroup-slider')], style = {'width' : '80%', 'padding' : '2px'})
    ], style = {'width' : '100vw', 'display': 'flex', 'align-items' : 'center', 'padding' : '4px'}),
    
    
    html.Div([dcc.Graph(id='model-score-test-graph', style = {'height' : 600})]),
])

featureImportance = html.Div([
    html.Div([
        html.Div(['特徵選擇'], style = {'font-size' : '18px', 'margin-left': '10px'}), 
        html.Div([dcc.Dropdown(
            feature_importance['Feature Id'].unique(),
            feature_importance['Feature Id'].unique().tolist()[0],
            searchable = True, multi = True, 
            id='feature-importance-dropdown'
        )], style={"width": "50%", 'margin-left': '20px'},)
    ], style = {'width' : '100vw', 'display': 'flex', 'align-items' : 'center', 'padding' : '2px', 'justify-content': 'start'}),
    
    html.Div([dcc.Graph(id='feature-importance-graph', style = {'height' : 800})]),
])

backTest = html.Div([
    # n_stock_slider
    
    html.Div([
        html.Div([dcc.Graph(figure = cumsum_ret_fig, id='cumsum-return-graph', style = {'height' : 800})], id = 'bt-graph-container', n_clicks = 0, style = {'width' : '60%'}),
        html.Div([initTable], id = 'click-data', style = {'width' : '20%'})], 
        style = {'width' : '100%', 'display': 'flex', 'align-items' : 'center', 'margin' : '10px'} ),
    
    html.Div([
        html.Div(['投資組合股票數量'], style = {'padding' : '3px', 'font-size' : '18px'}),
        html.Div([dcc.Slider(backtest_data['n_stock'].min(), 
                             backtest_data['n_stock'].max(), 
                             value=backtest_data['n_stock'].min(),
                             marks={str(backtest_data): str(backtest_data) for n_group in backtest_data['n_stock'].unique()},
                             step = 2,
                             id='nstk-slider')], style = {'width' : '80%', 'padding' : '2px'})
    ], style = {'width' : '100vw', 'display': 'flex', 'align-items' : 'center', 'padding' : '4px'}), 
    
    html.Div([
        html.Div(['資料選擇'], style = {'padding' : '3px', 'font-size' : '18px'}), 
        html.Div([dcc.RadioItems(['每月累積報酬率', '每月最大回撤','每月勝率'], '每月累積報酬率', inline=True, id = 'value-type-radio')], style = {'width' : '80%', 'padding' : '2px'})
    ], style = {'width' : '100%', 'display': 'flex', 'align-items' : 'center', 'padding' : '4px'}), 
    
    html.Div([
        html.Div([dcc.Graph(id='heatmap-graph', config = {'autosizable' : True})], style = {'width': '35%'}),
        html.Div([dcc.Graph(id='histogram-graph', config = {'autosizable' : True})], style = {'width': '35%'}),
    
    ], style = {'width' : '90%', 'display': 'flex', 'align-items' : 'center', 'padding' : '4px', 'flex-wrap' : 'wrap', 'justify-content' : 'space-around'})
#     html.Div([dcc.Graph(id='heatmap-graph')], style = {'padding' : '4px'}),
#     html.Div([dcc.Graph(id='histogram-graph')], style = {'padding' : '4px'}),
    
])

realWorld = html.Div([
    dcc.Graph(figure = fig, id = 'realworld-performance', style = {'height' : '80vh'})
])
mainIndex = html.Div([
    dcc.Tabs([
        dcc.Tab(label = '模型指標分組測試', children = [indicator_group_test]), 
        dcc.Tab(label = '特徵重要度', children = [featureImportance]), 
        dcc.Tab(label = '策略回測', children = [backTest]),
        dcc.Tab(label = '實單交易績效', children = [realWorld])
    ]), 
])

app = Dash(__name__)
app.layout = mainIndex
server = app.server

@callback(
    Output('model-score-test-graph', 'figure'),
    Input('ngroup-slider', 'value'), 
    Input('model-score-test_indicator-dropdown', 'value')
)
def update_model_score_test_graph(selected_nGroup, select_indicator):
    filtered_df = model_score[(model_score['nGroup'].astype('int') == int(selected_nGroup)) & (model_score['score_indicator'] == select_indicator)]
    title = f'每日將股票以{select_indicator}分數由高到低分{selected_nGroup}組，計算每組平均報酬率隨時間累加繪製成圖'
    fig = px.line(filtered_df, x="trading_datetime", y="group_cumsum_ret", color = 'group', title = title, height=800)
    return(fig)

@callback(
    Output('feature-importance-graph', 'figure'),
    Input('feature-importance-dropdown', 'value'), 
)
def update_feature_importance(features):
    if type(features) == type('string'):
        features = [features]
    filtered_df = feature_importance[feature_importance['Feature Id'].isin(features)].sort_values('model_id').reset_index(drop = True)
    title = f'不同時期模型之特徵重要度'
    fig = px.bar(filtered_df, x="model_id", y="Importances", color="Feature Id", title=title, barmode="group", height = 800)
    return(fig)

@callback(
    Output('heatmap-graph', 'figure'),
    Output('histogram-graph', 'figure'),
    Input('value-type-radio', 'value'), 
    Input('nstk-slider', 'value'), 
)
def update_heatmap_histogram_chart(value_type, n_stk):
    filterData = backtest_data[(backtest_data['n_stock'].astype('int') == int(n_stk))]
    title = f'{value_type}熱力圖，投資組合股票數量 = {n_stk}，多部位股票數 = {int(int(n_stk)/2)}，空部位股票數 = {int(int(n_stk)/2)}'
    titleHisto = f'{value_type}分配圖，投資組合股票數量 = {n_stk}，多部位股票數 = {int(int(n_stk)/2)}，空部位股票數 = {int(int(n_stk)/2)}'

    figHisto = px.histogram(filterData, x = 'ret_portfolio', histnorm='probability', marginal = 'box', 
                            title = titleHisto, width = 1000, height = 800)
    
    if value_type == '每月累積報酬率':
        filterData['ret_portfolio'] = filterData['ret_portfolio'].apply(lambda x: round(x, 4))
        heatMapData = filterData.groupby(['yr','mth'])['ret_portfolio'].sum().reset_index().sort_values([ 'mth', 'yr'], ascending = True)
        heatMapData = pd.pivot( heatMapData, index = 'yr', columns = 'mth', values = 'ret_portfolio')
        fig = px.imshow(heatMapData, color_continuous_scale='Tropic', title = title, color_continuous_midpoint=0, text_auto = True, width = 1000, height = 800)
    elif value_type == '每月最大回撤':
        heatMapData = filterData.groupby(['yr','mth'])['ret_portfolio_cumprod'].apply(lambda x: round((((1 + x)/(1 + x).cummax()) - 1).min(), 4) ).reset_index().sort_values([ 'mth', 'yr'], ascending = True)
        heatMapData = pd.pivot( heatMapData, index = 'yr', columns = 'mth', values = 'ret_portfolio_cumprod')
        fig = px.imshow(heatMapData, color_continuous_scale='Tropic', title = title, text_auto = True, width = 1000, height = 800)
        
    elif value_type == '每月勝率':
        heatMapData = filterData.groupby(['yr','mth'])['ret_portfolio'].apply(lambda x: round((x > 0).sum()/len(x), 3)).reset_index().sort_values([ 'mth', 'yr'], ascending = True)
        heatMapData = pd.pivot( heatMapData, index = 'yr', columns = 'mth', values = 'ret_portfolio')
        fig = px.imshow(heatMapData, color_continuous_scale='Tropic', title = title, color_continuous_midpoint=0.5, text_auto = True, width = 1000, height = 800)
    
    
    return(fig, figHisto)


@callback(
    Output('click-data', 'children'),
    Input('cumsum-return-graph', 'clickData')
)
def showClickData(clickdata):
    if clickdata:
        print('call')
        clickdata['points'][0]['curveNumber'] = clickdata['points'][0]['curveNumber'] + 1
        n_stk_single_side = clickdata['points'][0]['curveNumber']
        select_date = clickdata['points'][0]['x']
        cumsum_ret = clickdata['points'][0]['y']
        filterData = backtest_data[(backtest_data['trading_datetime'].astype('string') == select_date) & (backtest_data['n_stock'].astype('int') == int(n_stk_single_side * 2))]
        
        renameColname = {'trading_datetime' : '交易日期', 'ret_portfolio_cumsum' : '策略累積收益率', 'ret_portfolio' : '當日收益率', 
                 'ret_portfolio_dd' : '當日回撤', 'portfolio_max_drawdown': '策略最大回撤', 'long_stock' : '當日做多股票', 
                 'short_stock' : '當日做空股票', 
                 'long_short_corr' : '策略多空部位收益率相關性', 'ret_portfolio_winRate' : '策略勝率', 
                 'ret_portfolio_annualRet' : '策略年化收益率', 'VaR_5%_oneDay' : '策略5%VaR(天)'}
        showColumns = ['trading_datetime', 'ret_portfolio_cumsum', 'ret_portfolio', 'ret_portfolio_dd', 'long_stock', 'short_stock', 
                       'long_short_corr', 'ret_portfolio_winRate', 'ret_portfolio_annualRet', 'portfolio_max_drawdown', 'VaR_5%_oneDay']
        filterData['trading_datetime'] = filterData['trading_datetime'].astype('string')
        filterData = filterData[showColumns].rename(columns = renameColname).reset_index(drop = True).transpose().reset_index()
        filterData.columns = ['欄位', '數值']
        jsonData = filterData.to_dict('records')
        columns = [{"name" : i, 'id' : i} for i in filterData.columns]
        dataTable = dash_table.DataTable(jsonData, columns = columns, 
                                         style_data = {'color' : 'black', 'font_size' : '18px', 'textAlign' : 'left'}, 
                                         style_header = {'font_weight' : 'bold', 'color' : 'black', 'font_size' : '18px'})
        return(dataTable)

    
if __name__ == '__main__':
    app.run_server(debug=False)