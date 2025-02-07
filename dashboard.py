import panel as pn
import folium
import pandas as pd
import numpy as np
from folium import plugins
from bokeh.models import Div
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# City coordinates data
CITY_COORDS = {
    'Delhi': [28.6139, 77.2090],
    'Mumbai': [19.0760, 72.8777],
    'Bangalore': [12.9716, 77.5946],
    'Hyderabad': [17.3850, 78.4867],
    'Chennai': [13.0827, 80.2707],
    'Kolkata': [22.5726, 88.3639],
    'Ahmedabad': [23.0225, 72.5714],
    'Pune': [18.5204, 73.8567],
    'Jaipur': [26.9124, 75.7873],
    'Lucknow': [26.8467, 80.9462]
}

# Initialize Panel
pn.extension('plotly', sizing_mode="stretch_width", notifications=True)

# Load data
df = pd.read_csv("Fast Delivery Agent Reviews.csv")
df['Latitude'] = df['Location'].map(lambda x: CITY_COORDS[x][0])
df['Longitude'] = df['Location'].map(lambda x: CITY_COORDS[x][1])

# Create title pane
title = pn.pane.HTML("""
<div style="text-align: center; padding: 15px; 
            background: linear-gradient(135deg, #4f46e5, #3b82f6);
            color: white; border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;">
    <h1 style="font-size: 2rem; margin: 0; font-weight: 600;">🚚 India Delivery Service Analysis</h1>
    <div style="font-size: 1rem; margin-top: 8px; opacity: 0.9;">Made by Yanzhen Chen</div>
</div>
""")

# Create info panel
info_card = pn.pane.Markdown("""
### 📌 Guide
- 🔴 Red: Rating < 3.0
- 🟡 Yellow: 3.0 ≤ Rating < 4.0
- 🟢 Green: Rating ≥ 4.0
- 📍 Marker size proportional to order volume
""")

# Create filter widgets
agent_select = pn.widgets.Select(
    name='📦 Delivery Agent',
    options=['All'] + list(df['Agent Name'].unique()),
    value='All',
    width=240,
    styles={
        'font-size': '14px',
        'max-width': '100%',
        'box-sizing': 'border-box'
    }
)

order_type_select = pn.widgets.Select(
    name='📋 Order Type',
    options=['All'] + list(df['Order Type'].unique()),
    value='All',
    width=240,
    styles={
        'font-size': '14px',
        'max-width': '100%',
        'box-sizing': 'border-box'
    }
)

# 添加事件处理器（显示通知）
def on_change(event):
    pn.state.notifications.info('Updating dashboard...', duration=1000)

agent_select.param.watch(on_change, 'value')
order_type_select.param.watch(on_change, 'value')


# ----------------------------
# 内部函数不再使用 @pn.depends 装饰器
# ----------------------------

def create_map_pane(agent, order_type):
    """根据过滤器生成 Folium 地图，并返回 Panel HTML pane"""
    # 根据过滤条件过滤数据
    filtered_df = df.copy()
    if agent != 'All':
        filtered_df = filtered_df[filtered_df['Agent Name'] == agent]
    if order_type != 'All':
        filtered_df = filtered_df[filtered_df['Order Type'] == order_type]
    
    # 计算各城市统计数据
    city_stats = filtered_df.groupby('Location').agg({
        'Rating': 'mean',
        'Latitude': 'first',
        'Longitude': 'first',
        'Order Type': 'count'
    }).reset_index()
    
    # 创建地图
    m = folium.Map(
        location=[22.5726, 78.3639],
        zoom_start=4.5,
        tiles='CartoDB positron',
        control_scale=True
    )
    
    # 定义评分对应的颜色
    rating_colors = {
        'low': 'red',      # 评分低于3.0
        'medium': 'orange', # 评分3.0-4.0
        'high': 'green'    # 评分高于4.0
    }
    
    # 添加标记
    for _, row in city_stats.iterrows():
        if row['Rating'] < 3.0:
            icon_color = rating_colors['low']
        elif row['Rating'] < 4.0:
            icon_color = rating_colors['medium']
        else:
            icon_color = rating_colors['high']
        
        popup_html = f"""
        <div style="min-width: 200px; padding: 15px; font-family: Arial;">
            <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid {icon_color};">
                {row['Location']}
            </h4>
            <div style="margin: 10px 0;">
                <b>Rating:</b> {row['Rating']:.2f}/5<br>
                <b>Orders:</b> {row['Order Type']:,}
            </div>
        </div>
        """
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=icon_color, icon='info-sign'),
            tooltip=f"{row['Location']}: {row['Rating']:.1f}/5"
        ).add_to(m)
    
    return pn.pane.HTML(m._repr_html_(), height=600, sizing_mode='stretch_width')


def create_analytics_charts(filtered_df):
    """根据过滤后的数据生成 Plotly 饼图，并返回 Panel Plotly pane"""
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"type": "pie"}]]
    )
    
    # 计算订单量分布
    order_volume = filtered_df.groupby('Location')['Order Type'].count()
    
    # 定义柔和的颜色方案
    colors = ['#60a5fa', '#34d399', '#fbbf24', '#f87171', 
              '#818cf8', '#a78bfa', '#ec4899', '#2dd4bf',
              '#fb7185', '#a3e635']
    
    fig.add_trace(
        go.Pie(
            labels=order_volume.index,
            values=order_volume.values,
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>" +
                          "Orders: %{value}<br>" +
                          "Percentage: %{percent}<extra></extra>",
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            hole=0.4,
            rotation=90,
            showlegend=False
        )
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        margin=dict(l=50, r=30, t=20, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_traces(
        domain=dict(x=[0, 1.0], y=[0, 1.0]),
        textfont=dict(size=14)
    )
    
    return pn.pane.Plotly(fig, sizing_mode='stretch_both')


# ----------------------------
# 顶层依赖函数，统一监听过滤器变化
# ----------------------------
@pn.depends(agent_select.param.value, order_type_select.param.value)
def create_main_panel(agent, order_type):
    """主界面：包含地图与订单量饼图"""
    # 过滤数据
    filtered_df = df.copy()
    if agent != 'All':
        filtered_df = filtered_df[filtered_df['Agent Name'] == agent]
    if order_type != 'All':
        filtered_df = filtered_df[filtered_df['Order Type'] == order_type]
        
    return pn.Row(
        pn.Column(
            pn.pane.Markdown("### 🗺️ Delivery Service Rating Map", 
                             styles={'font-size': '18px', 'margin-bottom': '10px'}),
            create_map_pane(agent, order_type),  # 直接调用内部函数，传入参数
            width=800,
            height=600
        ),
        pn.Column(
            pn.pane.Markdown("### 📊 Order Volume Distribution",
                             styles={'font-size': '18px', 'margin-bottom': '10px', 'text-align': 'center'}),
            create_analytics_charts(filtered_df), 
            width=450,
            height=600,
            margin=(0, 0, 0, 30)
        ),
        sizing_mode='stretch_width'
    )


@pn.depends(agent_select.param.value, order_type_select.param.value)
def create_stat_cards(agent, order_type):
    """生成顶部统计信息卡片"""
    filtered_df = df.copy()
    if agent != 'All':
        filtered_df = filtered_df[filtered_df['Agent Name'] == agent]
    if order_type != 'All':
        filtered_df = filtered_df[filtered_df['Order Type'] == order_type]
    
    # 计算统计数据，注意对空数据的判断
    if not filtered_df.empty:
        top_city = filtered_df.groupby('Location')['Order Type'].count().idxmax()
        top_city_orders = filtered_df.groupby('Location')['Order Type'].count().max()
        top_rating_city = filtered_df.groupby('Location')['Rating'].mean().idxmax()
        top_city_rating = filtered_df.groupby('Location')['Rating'].mean().max()
    else:
        top_city, top_city_orders = 'N/A', 0
        top_rating_city, top_city_rating = 'N/A', 0

    cards = pn.Row(
        pn.Column(
            "### 🏆 Top Performing City",
            f"**{top_city}**",
            f"{top_city_orders:,} orders",
            styles={
                'background': '#f0f7ff',
                'padding': '15px',
                'border-radius': '8px',
                'text-align': 'center',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.08)'
            }
        ),
        pn.Column(
            "### ⭐ Highest Rated City",
            f"**{top_rating_city}**",
            f"{top_city_rating:.2f}/5 rating",
            styles={
                'background': '#f0f7ff',
                'padding': '15px',
                'border-radius': '8px',
                'text-align': 'center',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.08)'
            }
        ),
        sizing_mode='stretch_width',
        margin=(-40, 0, 0, 280),
        styles={
            'justify-content': 'flex-start'
        }
    )
    return cards


def create_analytics_dashboard():
    """构建整个仪表板，包括过滤器、主视图、统计信息与详细统计标签页"""
    @pn.depends(agent_select.param.value, order_type_select.param.value)
    def get_summary_stats(agent, order_type):
        filtered_df = df.copy()
        if agent != 'All':
            filtered_df = filtered_df[filtered_df['Agent Name'] == agent]
        if order_type != 'All':
            filtered_df = filtered_df[filtered_df['Order Type'] == order_type]
            
        return pn.pane.Markdown(f"""
        - **Total Orders:** {len(filtered_df):,}
        - **Average Rating:** {filtered_df['Rating'].mean():.2f}/5
        - **Cities Covered:** {filtered_df['Location'].nunique()}
        - **Active Agents:** {filtered_df['Agent Name'].nunique()}
        - **Most Common Order Type:** {filtered_df['Order Type'].mode().iloc[0] if not filtered_df.empty else 'N/A'}
        """)
    
    # 构建过滤器控制面板
    controls = pn.Column(
        pn.pane.Markdown('### 🔍 Filters', styles={'font-size': '16px'}),
        agent_select,
        order_type_select,
        info_card,
        pn.pane.Markdown("""
        ### 📊 Summary Statistics
        """, styles={'font-size': '16px', 'margin-top': '20px'}),
        get_summary_stats,
        width=280,
        width_policy='fixed',
        margin=(40, 20, 0, 0),
        styles={
            'background': '#f0f7ff',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.08)',
            'position': 'relative',
            'z-index': '1'
        }
    )
    
    # 创建主视图，将依赖函数直接传入
    main_view = pn.Column(
        pn.Row(
            controls,
            create_main_panel,
            sizing_mode='stretch_width'
        ),
        create_stat_cards,
        sizing_mode='stretch_width'
    )
    
    # 详细统计视图
    @pn.depends(agent_select.param.value, order_type_select.param.value)
    def create_detailed_stats(agent, order_type):
        filtered_df = df.copy()
        if agent != 'All':
            filtered_df = filtered_df[filtered_df['Agent Name'] == agent]
        if order_type != 'All':
            filtered_df = filtered_df[filtered_df['Order Type'] == order_type]
            
        detailed_controls = pn.Column(
            pn.pane.Markdown('### 🔍 Filters', styles={'font-size': '16px'}),
            agent_select,
            order_type_select,
            width=280,
            width_policy='fixed',
            margin=(0, 20, 0, 0),
            styles={
                'background': '#f0f7ff',
                'padding': '20px',
                'border-radius': '12px',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.08)'
            }
        )
        
        stats_panel = pn.Column(
            pn.pane.Markdown("### 📊 Detailed Statistics"),
            pn.pane.DataFrame(filtered_df.describe().round(2)),
            pn.pane.Markdown("### 📈 Order Type Distribution"),
            pn.pane.DataFrame(filtered_df['Order Type'].value_counts().reset_index()),
            width=800
        )
        
        return pn.Row(
            detailed_controls,
            stats_panel,
            sizing_mode='stretch_width'
        )
    
    # 创建标签页
    tabs = pn.Tabs(
        ('Dashboard', main_view),
        ('Detailed Stats', create_detailed_stats)
    )
    
    return tabs


# 最终布局
final_dashboard = pn.Column(
    title,
    create_analytics_dashboard(),
    sizing_mode='stretch_width',
    styles={
        'padding': '1rem',
        'background': 'white',
        'min-height': '95vh',
        'max-width': '1600px',  # 限制最大宽度
        'margin': '0 auto'      # 居中显示
    }
)

responsive_widget_style = """
    width: 100%; 
    max-width: 300px;  
    min-width: 220px;
    box-sizing: border-box;
    font-size: clamp(12px, 1.2vw, 14px);
"""

# 自定义 CSS 样式
if __name__ == '__main__':
    pn.extension(design='material', template='bootstrap')
    
    pn.config.raw_css += """
    .bk-panel-models-markdown-HTML {
        border-radius: 12px !important;
        background-color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
    }
    
    .bk-panel {
        background: transparent !important;
    }
    
    .widget-box {
        background-color: white !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        padding: 15px !important;
    }
    
    .chart-container {
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
        padding: 20px !important;
    }
    """
    
    pn.state.notifications.position = 'bottom-right'
    pn.config.throttled = False
    
    pn.serve(final_dashboard, show=True)
