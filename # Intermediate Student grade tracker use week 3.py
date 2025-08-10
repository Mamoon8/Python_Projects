# Intermediate Student grade tracker useing data types
""" This is a simple student grade tracker that uses basic data types like lists and dictionaries to store and manage student grades. but is a big step up from week 2"""
students = {}

def add_student():
    student_name = input("Enter the student's name: ")
    if student_name not in students:
        students[student_name] = []
    else:
        print("Student already exists.")

def add_grade():
    student_name = input("Enter the student's name: ")
    if student_name in students:
        grade = float(input(f"Enter a grade for {student_name}: "))
        students[student_name].append(grade)
    else:
        print("Student not found.")

def view_grades():
    student_name = input("Enter the student's name: ")
    if student_name in students:
        grades = students[student_name]
        if grades:
            print(f"Grades for {student_name}: {', '.join(map(str, grades))}")
        else:
            print(f"No grades found for {student_name}.")
    else:
        print("Student not found.")

def calculate_average():
    student_name = input("Enter the student's name: ")
    if student_name in students:
        grades = students[student_name]
        if grades:
            average = sum(grades) / len(grades)
            print(f"Average grade for {student_name}: {average:.2f}")
        else:
            print(f"No grades found for {student_name}.")
    else:
        print("Student not found.")

def remove_student():
    student_name = input("Enter the student's name to remove: ")
    if student_name in students:
        del students[student_name]
        print(f"Removed student: {student_name}")
    else:
        print("Student not found.")
def main():
    while True:
        print("Welcome to the Student Grade Tracker!")
        name = input("Enter the student's name (or 'exit' to quit): ")
        if name.lower() == "exit":
            break
        print("1. Add Student")
        print("2. Add Grade")
        print("3. View Grades")
        print("4. Calculate Average")
        print("5. Remove Student")
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            add_student()
        elif choice == "2":
            add_grade()
        elif choice == "3":
            view_grades()
        elif choice == "4":
            calculate_average()
        elif choice == "5":
            remove_student()
        else:
            print("Invalid choice. Please try again.")
