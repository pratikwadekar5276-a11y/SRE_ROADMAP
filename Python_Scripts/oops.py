from os import name


class job:
    position = "Software Engineer"
    name = "John Doe"
    org_name = "Tech Solutions Inc."
    salary = 75000

    def loan_eligibility(self):
        if self.salary > 50000:
            return "Eligible for loan"
        else:
            return "Not eligible for loan"

a = job()
a.name = "Pratik Wadekar"
try:
    print(a.position,a.name)
    print(a.loan_eligibility())
except AttributeError:
    print("Attribute 'position' not found in the job class.")

class Student:

    def info(self):
            print(self.name)



a = Student("Pratik")

b = Student("Pranav")

a.info()

b.info()
