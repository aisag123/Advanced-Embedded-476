from random import randint

def rollDice(num):
    roll = randint(1, num)
    return(roll)

def playerOne(rolls):
    player1 = 0
    for i in range(rolls):
        roll = rollDice(12)
        print("p1 roll", roll)
        player1 += roll
        print(player1)
    return(player1)
        
def playerTwo(rolls):
    player2 = 0
    for i in range(rolls):
        roll = rollDice(8)
        print("p2 roll", roll)
        player2 += roll
        print(player2)
    return(player2)
    
p1_total_w = 0
p2_total_w = 0
for i in range(0, 10000):
    p1 = playerOne(3)
    p2 = playerTwo(4)
    if p1 >= p2:
        p1_total_w += 1
    else:
        p2_total_w += 1
    print("player 1 wins", p1_total_w, "player 2 wins", p2_total_w)
