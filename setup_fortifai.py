
import subprocess
import sys
import os

def run_command(command, shell=False):
    result = subprocess.run(command, shell=shell)
    if result.returncode != 0:
        print(f"Error while executing: {' '.join(command) if isinstance(command, list) else command}")
        sys.exit(1)

def main():
    print("\nStarting full FortifAI system setup...\n")

    # Step 1: Create virtual environment (only if it doesn't exist)
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", "venv"])
    else:
        print(" Virtual environment already exists.")

    # Step 2: Activate venv (Windows-specific)
    print("\n IMPORTANT: Please activate the virtual environment manually before continuing:")
    print("On Windows: venv\\Scripts\\activate")
    print("On Mac/Linux: source venv/bin/activate")
    input("Press ENTER after you have activated the virtual environment...")

    # Step 3: Install requirements
    print("\nInstalling required Python packages...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Step 4: Generate Text/Image Pools
    #print("\nGenerating Listing Fraud Pools...")
    #run_command([sys.executable, "initialize_listing_text_image_pools.py"])

    # Step 5: Generate Account Behavioral Profiles
    print("\n Generating Behavioral Profiles...")
    run_command([sys.executable, "generate_full_account_profiles.py"])

    # Step 6: Train Behavioral Transaction Model
    print("\nTraining Behavioral Transaction Fraud Model...")
    run_command([sys.executable, "train_behaviour_model.py"])

    print("\nFortifAI full system setup completed successfully!")
    print("You can now run your Streamlit app.")

if __name__ == "__main__":
    main()
