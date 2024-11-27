import os
import subprocess
from datetime import datetime
from Logger import Logger  # Assuming Logger is defined elsewhere

class GitHandler:
    def __init__(self, repo_path=r'C:\Users\Administrator\Desktop\project-connecta'):
        self.repo_path = repo_path

    def commit_changes_to_git(self):
        try:
            # Ensure you're in the Git repository directory
            if not os.path.exists(os.path.join(self.repo_path, '.git')):
                Logger.log(f"Error: {self.repo_path} is not a valid Git repository.")
                return

            os.chdir(self.repo_path)  # Change working directory to repo

            # Check if there are changes to commit (i.e., untracked or modified files)
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True
            )

            # Debugging the status output to check the repository state
            Logger.log(f"Git status output: {status.stdout}")

            if status.returncode != 0:
                Logger.log(f"Error checking Git status: {status.stderr}")
                return

            # If there are no changes, exit early
            if not status.stdout.strip():
                Logger.log("No changes to commit.")
                return

            # Stage the changes (add all changes)
            add_result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True, text=True, check=True
            )
            Logger.log(f"Git add output: {add_result.stdout}")

            # Create a commit message with a timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f'Update pet profile data at {timestamp}'

            # Commit the changes with the timestamped message
            commit = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True, text=True, check=True
            )

            Logger.log(f"Git commit output: {commit.stdout}")

            # Optionally, push the changes to a remote repository
            push = subprocess.run(
                ['git', 'push', '--force'],
                capture_output=True, text=True, check=True
            )

            Logger.log(f"Git push output: {push.stdout}")

            Logger.log(f"Changes committed successfully with message: {commit_message}")

        except subprocess.CalledProcessError as e:
            Logger.log(f"Error during Git operation: {e}")
            Logger.log(f"Standard error output: {e.stderr}")
            Logger.log(f"Standard output: {e.stdout}")
        except Exception as e:
            Logger.log(f"Unexpected error: {e}")
