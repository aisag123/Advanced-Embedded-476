from random import randint

def rollDice(num):
    roll = randint(1, num)
    return(roll)

def playerOne(rolls):
    player1 = 0
    for i in range(rolls):
        roll = rollDice(12)
        player1 += roll
    return(player1)
        
def playerTwo(rolls):
    player2 = 0
    for i in range(rolls):
        roll = rollDice(8)
        player2 += roll
    return(player2)
    
p1_match_w = 0
p2_match_w = 0

for i in range(0, 10000):
    p1_match = 0
    p2_match = 0
    
    while True:
        p1 = playerOne(3)
        p2 = playerTwo(4)
        
        if p1 >= p2:
            p1_match += 1
        else:
            p2_match += 1
        
        if p1_match >= 5 and p1_match - p2_match >= 2:
            p1_match_w += 1
            break
        elif p2_match >= 5 and p2_match - p1_match >= 2:
            p2_match_w += 1
            break
        
    print("player 1 matches won", p1_match_w)
    print("player 2 matches won", p2_match_w)


