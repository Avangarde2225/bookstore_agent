import mlflow
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class MLflowTracker:
    def __init__(self):
        self.start_time = time.time()
        self.api_calls = 0
        self.api_tokens = 0
        self.api_costs = 0.0
        
    def log_api_call(self, model: str, tokens: int):
        """Log an API call with its token usage and cost"""
        self.api_calls += 1
        self.api_tokens += tokens
        
        # Calculate cost (approximate rates)
        cost_per_token = {
            "gpt-3.5-turbo": 0.000002,
            "gpt-4": 0.00003,
        }
        self.api_costs += tokens * cost_per_token.get(model, 0.00001)
        
        # Log to MLflow
        with mlflow.start_run(nested=True):
            mlflow.log_metrics({
                "api_calls": self.api_calls,
                "total_tokens": self.api_tokens,
                "total_cost_usd": self.api_costs,
                "tokens_per_call": tokens,
            })
            
            # Create and log cost visualization
            self._log_cost_visualization()
            
    def _log_cost_visualization(self):
        """Create and log cost tracking visualizations"""
        # Create a time series of costs
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'cost': [self.api_costs],
            'tokens': [self.api_tokens],
            'calls': [self.api_calls]
        })
        
        # Cost over time
        fig1 = px.line(df, x='timestamp', y='cost',
                      title='Cumulative API Costs Over Time')
        mlflow.log_figure(fig1, "cost_over_time.html")
        
        # Token usage distribution
        fig2 = go.Figure(data=[
            go.Bar(name='API Calls', x=['Metrics'], y=[self.api_calls]),
            go.Bar(name='Tokens (thousands)', x=['Metrics'], y=[self.api_tokens/1000])
        ])
        fig2.update_layout(title='API Usage Metrics')
        mlflow.log_figure(fig2, "api_usage.html")
        
        # Cost breakdown
        fig3 = px.pie(names=['API Costs', 'Other'],
                     values=[self.api_costs, 0.1],  # Adding minimal "Other" for perspective
                     title='Cost Breakdown')
        mlflow.log_figure(fig3, "cost_breakdown.html")
        
    def end_run(self):
        """End the tracking run and log final metrics"""
        execution_time = time.time() - self.start_time
        
        with mlflow.start_run(nested=True):
            mlflow.log_metrics({
                "total_execution_time": execution_time,
                "final_api_calls": self.api_calls,
                "final_tokens": self.api_tokens,
                "final_cost_usd": self.api_costs,
                "tokens_per_second": self.api_tokens / execution_time,
                "cost_per_call": self.api_costs / (self.api_calls if self.api_calls > 0 else 1)
            })
            
            # Log final visualizations
            self._log_cost_visualization()
            
            # Save cost to file for CI pipeline
            with open('api_cost_tracking.txt', 'w') as f:
                f.write(str(self.api_costs)) 