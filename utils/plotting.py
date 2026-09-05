import plotly.graph_objects as go
import plotly.express as px

def create_line_chart_with_events(df, x, y, events_df, title, yaxis_title):
    """Creates a line chart with vertical event markers."""
    fig = go.Figure()
    
    # Main line
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], mode='lines', name='Sentiment Intensity',
        line=dict(color='#1f77b4', width=3)
    ))
    
    # Event annotations
    if events_df is not None and not events_df.empty:
        for _, row in events_df.iterrows():
            fig.add_vline(
                x=row['date'], line_dash="dash", line_color="red", opacity=0.6,
                annotation_text=f"<b>{row['label']}</b><br>{row['category']}",
                annotation_position="top left"
            )
            
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        hovermode="x unified",
        template="plotly_white",
        height=600
    )
    return fig

def create_scatter_plot(df, x, y, color_col=None, title=None):
    """Creates a scatter plot with a trendline."""
    fig = px.scatter(
        df, x=x, y=y, color=color_col, trendline="ols",
        title=title, template="plotly_white", height=500
    )
    return fig