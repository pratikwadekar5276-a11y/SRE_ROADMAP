
import sys


a = sys.argv[1]
b = sys.argv[2]
c = sys.argv[3]

print(f"First argument: {a}")
print(f"Second argument: {b}")
print(f"Third argument: {c}")

for i in range(1, 10):
    print(f"Number: {i}")
    if i == 5:
        print("Breaking the loop at 5")
        sys.exit()  #Exit the program when i is 5
print("This line will not be executed because the program has exited.")
