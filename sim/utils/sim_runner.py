"""
sim_runner.py

Utility for running simulations and reading results in llm-sim.

Key Functions:
- run_simulation_and_read_results: Runs a simulation for a world and tick count, then reads metrics output.

LLM Usage:
- None

CLI Arguments:
- None (library module)
"""
import subprocess
import json
import os

def run_simulation_and_read_results(world_name: str, ticks: int = 100) -> dict:
    """
    Runs the simulation for the given world and tick count, then reads the metrics output.
    Args:
        world_name (str): Name of the world to simulate.
        ticks (int): Number of simulation ticks.
    Returns:
        dict: Parsed metrics from the simulation output.
    Raises:
        FileNotFoundError: If the metrics file is not found.
        RuntimeError: If the simulation run fails.
    """
    # Run the simulation using the CLI
    result = subprocess.run([
        'python', 'scripts/world_cli.py', 'run', world_name, '--ticks', str(ticks)
    ], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Simulation failed: {result.stderr}")
    # Locate metrics file
    metrics_path = os.path.join('outputs', 'llm_logs', f'{world_name}_metrics.json')
    if not os.path.exists(metrics_path):
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")
    # Read and parse metrics
    with open(metrics_path, 'r', encoding='utf-8') as f:
        metrics = json.load(f)
    return metrics
