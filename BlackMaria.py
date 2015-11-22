from Cards_0_2 import*

def score(cards):
    score = 0
    for c in cards:
        if c.suit == 2: score += 1
        elif c.suit == 3:
            if c.rank == 10: score += 13
            elif c.rank == 11: score += 10
            elif c.rank == 12: score += 7
    return score

def get_moves(game, player):
    hand = game.playerpiles[game.names.index(player)][0] #give the player the correct hand from playerpiles list
    try: suit = game.generalpiles[0][0].suit
    except IndexError: suit = None
    legalCards = []
    for c in hand:
        if c.suit == suit: legalCards.append(c)
    if legalCards == []: legalCards = hand[:]
    return legalCards

def play(game):
    if len(game.generalpiles[0]) == 4: game.generalpiles[0].clear()

    while len(game.generalpiles[0]) != 4:
        if game.move == None:
            game.move = game.players[game.turn].chooseCard(game) #hope this won't crash!
        card = game.move
        print("card:", card)
        game.move = None
        game.generalpiles[0].append(card)
        game.playerpiles[game.turn][0].remove(card)
        game.generalpiles[0].avalues.append(game.turn)
        game.turn = game.next(game.turn)

    suit = game.generalpiles[0][0].suit
    winning_cards = game.generalpiles[0][:]

    for c in game.generalpiles[0]:
        if c.suit != suit: winning_cards.remove(c)
    winning_card = max(winning_cards)
    print("Played cards: ", game.generalpiles[0])
    print("winning card: "+str(winning_card))

    winner = game.generalpiles[0].avalues[game.generalpiles[0].index(winning_card)]
    game.playerpiles[winner][1].extend(game.generalpiles[0])
    game.turn = winner
    print(winner)
    

Game.play = play #add play as method to Game class
Game.get_moves = get_moves

doc = """
Black Maria:
4 players.
default deck 52 cards.
scoring: Hearts = 1; Queen of Spades = 13; King of Spades = 10; Ace of Spades = 7.
Every player has a hand of 13 cards and a collection of won tricks.
In a trick everybody plays a card in to the middle (general pile).
Markers: dealer and round (0:passing cards, 1:playing, 2:scoring).
"""
deck = CardCollection(SDECK)
shuffle(deck)
game = Game([MCPlayer1(), RandomPlayer(), RandomPlayer(), RandomPlayer()], deck, score, [13, 0], [0], [0,1])

while game.playerpiles[0][0]!=[]:
    game.play()

print(game.score(game.playerpiles[0][1]))
print(game.score(game.playerpiles[1][1]))
print(game.score(game.playerpiles[2][1]))
print(game.score(game.playerpiles[3][1]))
