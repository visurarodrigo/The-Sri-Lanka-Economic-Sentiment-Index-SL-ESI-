import plotly.graph_objects as go
import plotly.express as px

def create_line_chart_with_events(df, x, y, events_df, title, yaxis_title):
    """Creates a line chart with vertical event markers and a legend."""
    fig = go.Figure()

    # Main line
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], mode='lines', name='Sentiment Intensity',
        line=dict(color='#1f77b4', width=3)
    ))

    # Event markers as traces for legend support
    if events_df is not None and not events_df.empty:
        # Determine y-range to make vertical lines span the plot
        y_min = df[y].min()
        y_max = df[y].max()

        # Use a diverse color palette for events
        colors = px.colors.qualitative.Plotly + px.colors.qualitative.Set1 + px.colors.qualitative.Pastel

        for i, (_, row) in enumerate(events_df.iterrows()):
            color = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=[row['date'], row['date']],
                y=[y_min, y_max],
                mode='lines',
                name=f"{row['label']} ({row['category']})",
                line=dict(color=color, width=2, dash='dash'),
                hoverinfo='name'
            ))

    fig.update_layout(
        title=title,
        xaxis=dict(title="Date", tickangle=45),
        yaxis_title=yaxis_title,
        hovermode="x unified",
        template="plotly_white",
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def create_scatter_plot(df, x, y, color_col=None, title=None):
    """Creates a scatter plot with a trendline."""
    fig = px.scatter(
        df, x=x, y=y, color=color_col, trendline="ols",
        title=title, template="plotly_white", height=500
    )
    return fig