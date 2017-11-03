class Pet:
  types = ['dog', 'cat']
  
  def __init__(self):
    self.__name = ''
    self.__animal = ''
    self.__age = 0
    
  def get_name(self):
    return self.__name
    
  def set_name(self, name):
    self.__name = name
    
  def set_animal(self, animal):
    if animal in self.__class__.types:
      self.__animal = animal
    
    else:
      print('Pet ' + animal + ' is not a valid pet type!')
      quit()
      #self.__animal = 'Unknown'
    
  def get_animal(self):
    return self.__animal
  
  def get_age(self):
    return self.__age
    
  def set_age(self, age):
    self.__age = age
    
  

pet_name = input("Enter pet name: ")

while True:
  try:
    pet_age = int(input("Enter pet age: "))
    break
  except Exception:
    print('Please enter a valid age.')
    
pet_type = input("Enter pet type: ")

pet = Pet()
pet.set_name(pet_name)
pet.set_age(pet_age)
pet.set_animal(pet_type)

print("Pet %s is a %s, it is %d years old" %(pet.get_name(), pet.get_animal(), pet.get_age()))


