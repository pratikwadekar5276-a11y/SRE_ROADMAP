import subprocess 
import sys

subject = sys.argv[1]
date = sys.argv[2]

subprocess.run(['ls','-lrt'])

subprocess.run(["git", "status"])

subprocess.run(["git", "add", "."])

subprocess.run(["git", "commit", "-m", "Python 28 June 2026"])

subprocess.run(["git", "push"])


