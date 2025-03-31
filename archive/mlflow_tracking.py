import mlflow
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import openai

class MLflowTracker:
    def __init__(self):
        self.start_time = time.time()
        self.api_calls = 0
        self.api_tokens = 0
        self.api_costs = 0.0
        self.cost_per_token = {
            "gpt-3.5-turbo": {
                "input": 0.0000015,
                "output": 0.000002
            },
            "gpt-4": {
                "input": 0.00003,
                "output": 0.00006
            }
        }
        
    def calculate_cost(self, model_name: str, total_tokens: int, input_tokens: int = None, output_tokens: int = None) -> float:
        """Calculate the cost of API usage"""
        if model_name not in self.cost_per_token:
            return 0.0
            
        if input_tokens is None:
            # Estimate input/output split if not provided
            input_tokens = int(total_tokens * 0.7)
            output_tokens = total_tokens - input_tokens
            
        cost = (input_tokens * self.cost_per_token[model_name]["input"] +
                output_tokens * self.cost_per_token[model_name]["output"])
        return cost

    def log_api_call(self, model: str, tokens: int, input_tokens: int = None, output_tokens: int = None):
        """Log API call details to MLflow"""
        with mlflow.start_run(nested=True):
            # Enable OpenAI autologging
            mlflow.openai.autolog()
            
            # Log basic metrics
            mlflow.log_metric(f"tokens_{model}", tokens)
            
            # Calculate and log costs
            cost = self.calculate_cost(model, tokens, input_tokens, output_tokens)
            mlflow.log_metric(f"cost_{model}", cost)
            
            # Log detailed information
            mlflow.log_dict({
                "model": model,
                "total_tokens": tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "timestamp": datetime.now().isoformat()
            }, "api_call_details.json")

    def start_run(self, run_name=None):
        """Start a new MLflow run"""
        return mlflow.start_run(run_name=run_name)

    def end_run(self):
        """End the current MLflow run"""
        mlflow.end_run()

    def log_feature_file(self, feature_file: str, content: str):
        """Log a feature file as an artifact"""
        with mlflow.start_run(nested=True):
            mlflow.log_text(content, feature_file)

    def log_step_definition(self, step_file: str, content: str):
        """Log a step definition file as an artifact"""
        with mlflow.start_run(nested=True):
            mlflow.log_text(content, f"step_definitions/{step_file}")

    def log_scenario_metrics(self, feature_name: str, total_scenarios: int, e2e_scenarios: int):
        """Log scenario metrics"""
        with mlflow.start_run(nested=True):
            mlflow.log_metric(f"{feature_name}_total_scenarios", total_scenarios)
            mlflow.log_metric(f"{feature_name}_e2e_scenarios", e2e_scenarios)

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

    def log_llm_metrics(self, model_name: str, tokens: int, input_tokens: int = None, output_tokens: int = None):
        """Log LLM usage metrics to MLflow"""
        with mlflow.start_run(nested=True):
            # Enable OpenAI autologging
            mlflow.openai.autolog()
            
            # Log basic metrics
            mlflow.log_metric(f"tokens_{model_name}", tokens)
            if input_tokens:
                mlflow.log_metric(f"input_tokens_{model_name}", input_tokens)
            if output_tokens:
                mlflow.log_metric(f"output_tokens_{model_name}", output_tokens)
            
            # Calculate and log costs
            cost = self.calculate_cost(model_name, tokens, input_tokens, output_tokens)
            mlflow.log_metric(f"cost_{model_name}", cost)
            
            # Log detailed information
            mlflow.log_dict({
                "model": model_name,
                "total_tokens": tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "timestamp": datetime.now().isoformat()
            }, f"llm_usage_{model_name}.json") 