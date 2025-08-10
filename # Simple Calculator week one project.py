# Simple Calculator 
""" This is a multiline comment and this is here just for explanation that many different way exist of making this but this is the most clean looking but maybe more complex than required"""
while True:
    print("Welcome to Simple Calculator App!")
    name = input("Enter your Name: ")
    print(f"Hello {name}, let's do some calculations!")

    # Get user input for the first number
    num1 = float(input("Enter the first number: "))

    # Get user input for the second number
    num2 = float(input("Enter the second number: "))

    # Get user input for the operation
    operation = input("Enter the operation (+, -, *, /): ")

    # Perform the calculation based on the operation
    if operation == "+":
        result = num1 + num2
    elif operation == "-":
        result = num1 - num2
    elif operation == "*":
        result = num1 * num2
    elif operation == "/":
        if num2 != 0:
            result = num1 / num2
        else:
            result = "Error: Division by zero is not allowed."
    else:
        result = "Error: Invalid operation."

    # Display the result
    print(f"The result of {num1} {operation} {num2} is: {result}")

    # Ask the user if they want to perform another calculation
    another = input("Do you want to perform another calculation? (yes/no): ")
    if another.lower() != "yes":
        break
