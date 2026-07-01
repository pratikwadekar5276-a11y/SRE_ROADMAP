space = input("Enter the space utilization: ")

try:
    if int(space) < 80:
        print("Space utilization is within acceptable limits.")
    elif int(space) >= 80 and int(space) < 90:
        print("Warning: Space utilization is high.")
    elif int(space) >= 90:
        print("Critical: Space utilization is very high.")
except Exception as e:
    print("An error occurred:", e)
finally:
    print("Space utilization check completed you can proceed with further actions.")