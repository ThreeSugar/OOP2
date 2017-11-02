import Owner as o
import Phone as p

database = {}
running = True

while running:

    input_phone = input("What is your desired phone number?")
    input_name = input("What is your name?")
    input_email = input("What is your email?")
    
    if input_phone in database:
         print("The number is not avaliable, please try again.")

    else:
         database.update({input_phone:input_name})
         print("The number " + input_phone + " has been assigned to " + input_name)

         break_input = input("Do you wish to quit the program? Enter y to quit or any other key to continue.").lower()
         if break_input == "y":
             running = False
         else:
             pass





        
        
         
        


       


        
         
    
   
        
       



   
        











