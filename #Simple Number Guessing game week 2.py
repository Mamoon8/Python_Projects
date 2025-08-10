#Simple Number Guessing game
""" This code uses some advanced principles but the general build is simple and beginner-friendly"""
import random

while True:
    print("Welcome to the Number Guessing Game!")
    name = input("Enter Your Name: ")
    print(f"Hello {name}, let's play!")

    # Generate a random number between 1 and 100
    secret_number = random.randint(1, 100)
    attempts = 0

    while True:
        guess = int(input("Enter your guess (between 1 and 100): "))
        attempts += 1

        if guess < secret_number:
            print("Too low! Try again.")
        elif guess > secret_number:
            print("Too high! Try again.")
        else:
            print(f"Congratulations {name}! You've guessed the number {secret_number} in {attempts} attempts.")
            break

    # Ask the user if they want to play again
    play_again = input("Do you want to play again? (yes/no): ")
    if play_again.lower() != "yes":
        break

