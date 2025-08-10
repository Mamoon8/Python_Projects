#Pet care Sim using objects
""" 
This is a more advanced topic so if you struggle use this as a guide or a reference
"""
class Pet:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.hunger = 0
        self.happiness = 100

    def feed(self):
        if self.hunger > 0:
            self.hunger -= 1
            print(f"{self.name} has been fed.")
        else:
            print(f"{self.name} is not hungry.")

    def play(self):
        if self.happiness < 100:
            self.happiness += 10
            print(f"{self.name} is playing and is now happier!")
        else:
            print(f"{self.name} is already very happy!")

    def __str__(self):
        return f"{self.name} the {self.species} (Hunger: {self.hunger}, Happiness: {self.happiness})"

def add_pet():
    name = input("Enter the pet's name: ")
    species = input("Enter the pet's species: ")
    pet = Pet(name, species)
    pets.append(pet)
    print(f"{name} the {species} has been added to your pets.")

def view_pets():
    if not pets:
        print("You have no pets.")
    else:
        print("Your pets:")
        for pet in pets:
            print(f" - {pet}")

def feed_pet():
    if not pets:
        print("You have no pets.")
        return
    name = input("Enter the pet's name: ")
    for pet in pets:
        if pet.name == name:
            pet.feed()
            return
    print(f"No pet found with the name {name}.")

def play_with_pet():
    if not pets:
        print("You have no pets.")
        return
    name = input("Enter the pet's name: ")
    for pet in pets:
        if pet.name == name:
            pet.play()
            return
    print(f"No pet found with the name {name}.")


def main():
    pets = []
    while True:
        print("Welcome to the Pet Care Simulator!")
        print("1. Add Pet")
        print("2. View Pets")
        print("3. Feed Pet")
        print("4. Play with Pet")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            add_pet()
        elif choice == "2":
            view_pets()
        elif choice == "3":
            feed_pet()
        elif choice == "4":
            play_with_pet()
        elif choice == "5":
            print("Thank you for using the Pet Care Simulator!")
            break
        else:
            print("Invalid choice. Please try again.")
