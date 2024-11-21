import subprocess

def execute_module(module_name):

    try:
        print(f"Executing module: {module_name}")
        result = subprocess.run(
            ["python", "-m", module_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Module '{module_name}' executed successfully.\nOutput:\n{result.stdout}")
        else:
            print(f"Error executing module '{module_name}'.\nError:\n{result.stderr}")
    except Exception as e:
        print(f"An error occurred while executing module '{module_name}': {e}")

def main():
    """
    Main function to execute the list of modules in sequence.
    """
    modules_to_execute = [
        "dataFetcher.fetch_team_info",
        "dataFetcher.fetch_match_stats",
        "dataFetcher.fetch_odds_ranks",
        "executor.generate_prompts"
    ]
    
    for module in modules_to_execute:
        execute_module(module)

if __name__ == "__main__":
    main()
