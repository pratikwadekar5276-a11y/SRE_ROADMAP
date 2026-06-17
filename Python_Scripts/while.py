a = int(input("Enter the Number: "))
c = a
sum = 0
while(a>0):
    b = a%10
    sum = (sum*10)+b
    a = a // 10
else:
    print("Iteration is complted checking the number is palindrome or not")

print(sum)
if c == sum:
    print("Number is Palindrome")
else:
    print("Number is not Palindrome")