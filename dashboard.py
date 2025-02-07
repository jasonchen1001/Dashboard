import panel as pn
import folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from bokeh.palettes import Category10
from delivery_api import DeliveryAPI

# Initialize Panel
pn.extension('plotly', sizing_mode="stretch_width", notifications=True)

# Initialize API
delivery_api = DeliveryAPI("Fast Delivery Agent Reviews.csv")

# Create title pane
title = pn.pane.HTML("""
<div style="text-align: center; padding: 15px; background: #4f46e5; color: white; border-radius: 12px;">
    <h1 style="font-size: 2rem; margin: 0;">🚚 India Delivery Service Analysis</h1>
    <div style="margin-top: 8px;">Made by Yanzhen Chen</div>
</div>
""")

# Create info panel
info_card = pn.pane.Markdown("""
### 📌 Guide
- 🔴 Red: Rating < 3.0
- 🟡 Yellow: 3.0 ≤ Rating < 4.0
- 🟢 Green: Rating ≥ 4.0
- 📍 Marker size proportional to order volume
""", styles={'font-size': '12px'})

# Create global filter controls for each tab
def create_dashboard_filters():
    return (
        pn.widgets.Select(
            name='📦 Delivery Agent',
            options=['All'] + list(delivery_api.data['Agent Name'].unique()),
            value='All',
            sizing_mode='stretch_width',
            styles={
                'font-size': '14px',
                'max-width': '200px',
                'box-sizing': 'border-box'
            }
        ),
        pn.widgets.Select(
            name='📋 Order Type',
            options=['All'] + list(delivery_api.data['Order Type'].unique()),
            value='All',
            sizing_mode='stretch_width',
            styles={
                'font-size': '14px',
                'max-width': '200px',
                'box-sizing': 'border-box'
            }
        )
    )

# Create global filter controls
dashboard_agent_select, dashboard_order_type_select = create_dashboard_filters()
stats_agent_select, stats_order_type_select = create_dashboard_filters()

# Add notification callback
def on_change(event):
    pn.state.notifications.info('Updating dashboard...', duration=1000)

dashboard_agent_select.param.watch(on_change, 'value')
dashboard_order_type_select.param.watch(on_change, 'value')
stats_agent_select.param.watch(on_change, 'value')
stats_order_type_select.param.watch(on_change, 'value')

# Modify create_analytics_dashboard function
def create_analytics_dashboard():
    """Build a complete dashboard with tabs"""
    # Use global filters
    @pn.depends(dashboard_agent_select.param.value, dashboard_order_type_select.param.value)
    def dashboard_panel(agent, order_type):
        return create_main_panel(agent, order_type)
    
    @pn.depends(stats_agent_select.param.value, stats_order_type_select.param.value)
    def stats_panel(agent, order_type):
        return create_detailed_stats(agent, order_type)
    
    tabs = pn.Tabs(
        ('Dashboard', dashboard_panel),
        ('Detailed Stats', stats_panel)
    )
    return tabs

def create_map_pane(agent, order_type):
    """Generate Folium map based on filters and return Panel HTML pane"""
    city_stats = delivery_api.get_city_stats(agent, order_type)
    
    # Create map
    m = folium.Map(
        location=[22.5726, 78.3639],
        zoom_start=4.5,
        tiles='CartoDB positron',
        control_scale=True
    )
    
    # Define colors for ratings
    rating_colors = {
        'low': 'red',      # Rating < 3.0
        'medium': 'orange', # 3.0 ≤ Rating < 4.0
        'high': 'green'    # Rating ≥ 4.0
    }
    
    # Add markers
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
    
    return pn.pane.HTML(m._repr_html_(), sizing_mode='stretch_both')

@pn.depends(dashboard_agent_select.param.value, dashboard_order_type_select.param.value)
def create_main_panel(agent, order_type):
    """Main interface: includes map and order volume pie chart"""
    filtered_df = delivery_api.get_filtered_data(agent, order_type)
    
    controls = pn.Column(
        pn.pane.Markdown('### 🔍 Filters', styles={'font-size': '14px', 'margin-bottom': '2px'}),
        dashboard_agent_select,
        dashboard_order_type_select,
        info_card,
        pn.pane.Markdown("""
        ### 📊 Summary Statistics
        """, styles={'font-size': '12px', 'margin-top': '0px', 'margin-bottom': '0px'}),
        pn.pane.Markdown(f"""
        - **Total Orders:** {len(filtered_df):,}
        - **Average Rating:** {filtered_df['Rating'].mean():.2f}/5
        - **Active Agents:** {filtered_df['Agent Name'].nunique()}
        - **Most Common Order Type:** {filtered_df['Order Type'].mode().iloc[0] if not filtered_df.empty else 'N/A'}
        """, styles={'margin-top': '0px', 'font-size': '12px'}),
        sizing_mode='stretch_width',
        styles={
            'flex-basis': '20%',
            'min-width': '200px',
            'max-width': '300px',
            'background': '#f0f7ff',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.08)',
            'position': 'relative',
            'z-index': '1'
        }
    )
    
    map_pane = create_map_pane(agent, order_type)
    chart_pane = create_analytics_charts(agent, order_type)
    stat_cards = create_stat_cards(agent, order_type)
    
    main_content = pn.Row(
        pn.Column(
            pn.pane.Markdown("### 🗺️ Delivery Service Rating Map", 
                           styles={'font-size': '14px', 'margin-bottom': '2px'}),
            map_pane,
            sizing_mode='stretch_both',
            styles={
                'flex-basis': '65%', 
                'flex-grow': '1',
                'height': '70vh'
            }
        ),
        pn.Column(
            pn.pane.Markdown("### 📊 Order Volume Distribution",
                           styles={'font-size': '14px', 'margin-bottom': '2px', 'text-align': 'center'}),
            chart_pane,
            sizing_mode='stretch_both',
            styles={
                'flex-basis': '35%', 
                'flex-grow': '1',
                'height': '70vh'
            }
        ),
        sizing_mode='stretch_both'
    )
    
    return pn.Column(
        pn.Row(
            controls,
            main_content,
            sizing_mode='stretch_width'
        ),
        stat_cards,
        sizing_mode='stretch_width'
    )

@pn.depends(stats_agent_select.param.value, stats_order_type_select.param.value)
def create_detailed_stats(agent, order_type):
    """Detailed statistics view"""
    filtered_df = delivery_api.get_filtered_data(agent, order_type)
        
    detailed_controls = pn.Column(
        pn.pane.Markdown('### 🔍 Filters', styles={'font-size': '16px'}),
        stats_agent_select,
        stats_order_type_select,
        sizing_mode='stretch_width',
        styles={
            'flex-basis': '20%',
            'min-width': '200px',
            'max-width': '300px',
            'background': '#f0f7ff',
            'padding': '20px',
            'border-radius': '12px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.08)'
        }
    )
    
    order_type_counts = delivery_api.get_order_type_distribution(agent, order_type)
    
    stats_panel = pn.Column(
        pn.pane.Markdown("### 📊 Detailed Statistics"),
        pn.pane.DataFrame(filtered_df.describe().round(2)),
        pn.pane.Markdown("### 📈 Order Type Distribution"),
        pn.pane.DataFrame(order_type_counts, index=False),  
        sizing_mode='stretch_width',
        styles={'flex-basis': '80%'}
    )
    
    return pn.Row(
        detailed_controls,
        stats_panel,
        sizing_mode='stretch_width'
    )

def create_analytics_charts(agent, order_type):
    """Generate Plotly pie chart based on filtered data"""
    filtered_df = delivery_api.get_filtered_data(agent, order_type)
    
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"type": "pie"}]]
    )
    
    # Calculate order volume distribution
    order_volume = filtered_df.groupby('Location')['Order Type'].count()
    
    # Use Panel's built-in color palette
    colors = Category10[10]
    
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
        height=None,
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

def create_stat_cards(agent, order_type):
    """Generate top statistics cards"""
    stats = delivery_api.get_top_stats(agent, order_type)
    
    cards = pn.Row(
        pn.Column(
            "### 🏆 Top Performing City",
            f"**{stats['top_city']}**",
            f"{stats['top_city_orders']:,} orders",
            styles={
                'background': '#f0f7ff',
                'padding': '10px',
                'border-radius': '8px',
                'text-align': 'center',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.08)',
                'font-size': '14px'
            }
        ),
        pn.Column(
            "### ⭐ Highest Rated City",
            f"**{stats['top_rating_city']}**",
            f"{stats['top_city_rating']:.2f}/5 rating",
            styles={
                'background': '#f0f7ff',
                'padding': '10px',
                'border-radius': '8px',
                'text-align': 'center',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.08)',
                'font-size': '14px'
            }
        ),
        sizing_mode='stretch_width',
        styles={
            'flex-wrap': 'wrap',
            'gap': '1rem',
            'justify-content': 'center'
        }
    )
    return cards

# Modify final layout
final_dashboard = pn.Column(
    title,
    create_analytics_dashboard(),
    sizing_mode='stretch_width',
    styles={
        'padding': '1rem',
        'background': 'white',
        'min-height': '95vh',
        'max-width': '90vw',
        'margin': '0 auto'
    }
)

if __name__ == '__main__':
    pn.extension(design='material', template='bootstrap')
    
    pn.state.notifications.position = 'bottom-right'
    pn.config.throttled = False
    
    pn.serve(final_dashboard, show=True)
