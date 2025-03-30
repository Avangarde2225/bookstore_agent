import mlflow
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Example data
dates = [datetime.now() - timedelta(hours=i) for i in range(10)]
costs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
tokens = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
calls = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

df = pd.DataFrame({
    'timestamp': dates,
    'cost': costs,
    'tokens': tokens,
    'calls': calls
})

# Cost Over Time
fig1 = px.line(df, x='timestamp', y='cost',
               title='Cumulative API Costs Over Time',
               labels={'cost': 'Cost (USD)', 'timestamp': 'Time'})
fig1.write_image("docs/cost_over_time.png")

# API Usage Distribution
fig2 = go.Figure(data=[
    go.Bar(name='API Calls', x=['Metrics'], y=[sum(calls)]),
    go.Bar(name='Tokens (thousands)', x=['Metrics'], y=[sum(tokens)/1000])
])
fig2.update_layout(title='API Usage Metrics')
fig2.write_image("docs/api_usage.png")

# Cost Breakdown
fig3 = px.pie(names=['API Costs', 'Other'],
              values=[sum(costs), 0.1],
              title='Cost Breakdown')
fig3.write_image("docs/cost_breakdown.png")

# Model-specific costs
model_costs = {
    'GPT-3.5-turbo': 0.6,
    'GPT-4': 0.4
}

fig4 = px.pie(names=list(model_costs.keys()),
              values=list(model_costs.values()),
              title='Cost Distribution by Model')
fig4.write_image("docs/model_costs.png")

# Token usage by model
model_tokens = {
    'GPT-3.5-turbo': 6000,
    'GPT-4': 4000
}

fig5 = px.bar(x=list(model_tokens.keys()),
              y=list(model_tokens.values()),
              title='Token Usage by Model',
              labels={'x': 'Model', 'y': 'Tokens'})
fig5.write_image("docs/model_tokens.png") 