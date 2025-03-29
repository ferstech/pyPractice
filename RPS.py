import random

possibleChoices = ["Rock", "Paper", "Scissors"]
# The computer randomly selects one of the three options
gamechoice = random.choice(possibleChoices)

UserChoice = input("Select your choice Rock Paper Scissors: ");

won = ""
if UserChoice == gamechoice:
    won = "We tied"
elif UserChoice == "Rock" and gamechoice == "Paper":
    won = "You Lost"
elif UserChoice == "Rock" and gamechoice == "Scissors":
    won = "You Win"
elif UserChoice == "Paper" and gamechoice == "Scissors":
    won = "You Lost"
elif UserChoice == "Paper" and gamechoice == "Rock":
    won = "You Win"
elif UserChoice =="Scissors" and gamechoice == "Rock" :
    won = "You Loose"
elif UserChoice == "Scissors" and gamechoice =="Paper":
     won = "You Win"
else:
    print( "Invalid Option")
print (f"You Picked {UserChoice} and I chose {gamechoice}")
print (won)
   