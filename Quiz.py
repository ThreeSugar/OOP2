import random

class Question:
    question_bank = {'What is 1 + 1 ?' : '2', 'What is 2 + 3 ?': '5',
    'What is 5 + 5 ?' : '10', 'Is fish a mammal ?' : 'no', 'Can a cockroach fly ?' : 'yes',
    }


class Quiz(Question):
    score = 0

    def start():
        qns = []
        for q in Question.question_bank:
            qns.append(q)
        selected_qns = random.sample(qns, 3)

        qn1 = input(selected_qns[0]).lower()
        if qn1 in Question.question_bank.values():
            Quiz.score += 1
            print('Points accumulated: '+ str(Quiz.score))
            print('Answer is: ' + Question.question_bank[selected_qns[0]])
        else:
            print("That was the wrong answer!")

        qn2 = input(selected_qns[1]).lower()
        if qn2 in Question.question_bank.values():
            Quiz.score += 1
            print('Points accumulated: '+ str(Quiz.score))
            print('Answer is: ' + Question.question_bank[selected_qns[1]])
        else:
            print("That was the wrong answer!")

        qn3 = input(selected_qns[2]).lower()
        if qn3 in Question.question_bank.values():
            Quiz.score += 1
            print('Points accumulated: '+ str(Quiz.score))
            print('Answer is: ' + Question.question_bank[selected_qns[2]])
        else:
            print("That was the wrong answer!")


Quiz.start()

        







        


    




    

