import subprocess 
import sys

subject = sys.argv[1]
date = sys.argv[2]
Month = sys.argv[3]
Year = sys.argv[4]

subprocess.run(['ls','-lrt'])

subprocess.run(["git", "status"])

subprocess.run(["git", "add", "."])

subprocess.run(["git", "commit", "-m", f"{subject} - {date} {Month} {Year}"])

subprocess.run(["git", "push"])


