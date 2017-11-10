import re

class Person:
    def __init__(self, ic, name):
        self.ic = ic
        self.name = name

    def __str__(self):
        return 'Name: ' + self.name + ' NRIC ' + self.ic

class Employee(Person):
    def __init__(self, ic, name, salary):
        super().__init__(ic, name)
        self.salary = salary

    def __str__(self):
        return super().__str__() + 'Salary: ' + self.salary


class Student(Person):
    def __init__(self, ic, name, gpa):
        super().__init__(ic, name)
        self.gpa = gpa

    def __str__(self):
        return "Name: " + self.name + ' NRIC: ' + self.ic + ' GPA: ' + self.gpa


emp_data = {}
stu_data = {}

running = True

while running:

        while True:
            try:
                user_nric = input('Enter NRIC: ')
                match = re.search('(?i)^[STFG]\d{7}[A-Z]$', user_nric)
                if match:
                    break
                else:
                    raise ValueError
            except ValueError:
                print('Invalid NRIC')

        user_name = input('Enter Name: ')
        choice = input('Student or Employee? (S or E)').lower()

        if choice == 's':
            while True:
                try:
                    get_gpa = float(input('Enter GPA: '))
                    break
                except ValueError:
                    print('Invalid GPA!')

            students = Student(user_nric, user_name, str(get_gpa))
            stu_data[user_nric] = students
            quits = input("Do you wish to quit? Y/N").lower()

            if quits == 'y':
                running = False
            else:
                pass

        elif choice == 'e':
            while True:
                try:
                    get_salary = float(input('Enter Salary: '))
                    break
                except ValueError:
                    print('Invalid input!')
                    
            employees = Employee(user_nric, user_name, str(get_salary))
            emp_data[user_nric] = employees
            quits = input("Do you wish to quit? Y/N").lower()

            if quits == 'y':
                running = False
            else:
                pass

        else:
            print('Please enter a valid input!')


for key in emp_data:
    print(emp_data[key])

for key in stu_data:
print(stu_data[key])
