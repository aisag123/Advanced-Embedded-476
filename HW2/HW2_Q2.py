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
    p1_games = 0
    p2_games = 0
    
    for j in range(5):
        p1 = playerOne(3)
        p2 = playerTwo(4)
        
        if p1 >= p2:
            p1_games += 1
        else:
            p2_games += 1
    
    if p1_games > p2_games:
        p1_match_w += 1
    else:
        p2_match_w += 1
        
    print("player 1 matches won", p1_match_w)
    print("player 2 matches won", p2_match_w)

