import subprocess
import time
import os

def run_command(command, description):
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"{'='*50}")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error in {description}: {str(e)}")
        return False

def main():
    # Create visualizations directory if it doesn't exist
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    
    # Check if model already exists
    model_exists = os.path.exists('enhanced_model.pt')
    
    # Define pipeline steps
    steps = [
        ("python dataset_stats.py", "Dataset Analysis")
    ]
    
    # Only add model training if model doesn't exist
    if not model_exists:
        steps.append(("python enhanced_model.py", "Model Training"))
    else:
        print("\n💡 Model already trained, skipping training step...")
    
    # Add visualization and web server steps
    steps.extend([
        ("python plot_metrics.py", "Generate Visualizations"),
        ("python app.py", "Start Web Server")
    ])
    
    # Run each step
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Pipeline failed at: {description}")
            break
        time.sleep(2)  # Small delay between steps
    
    print("\nAccess the web interface at http://localhost:5000")

if __name__ == "__main__":
    main()
