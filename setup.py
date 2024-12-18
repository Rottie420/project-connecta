import subprocess

def install_requirements():
    """Install modules from requirements.txt using py -m pip."""
    try:
        print("Installing modules from requirements.txt...")
        subprocess.check_call(["py", "-m", "pip", "install", "-r", "requirements.txt"])
        print("All modules installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing modules: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    install_requirements()
