from random import shuffle, randint, choice
import sys #only for setrecursionlimit

SUITS = ["Clubs", "Diamonds", "Hearts", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

ITERMAX = 2 #MC iterations
sys.setrecursionlimit(5000) #TODO check algorithm

VERBOSE = False #Some players have a verbose setting

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    def __str__(self):
        return "%s of %s" %(RANKS[self.rank],SUITS[self.suit])
    def __lt__(self, other):
        if self.suit < other.suit: return True
        elif self.suit > other.suit: return False
        elif self.rank < other.rank: return True
        else: return False
    def __gt__(self, other):
        if self.suit > other.suit: return True
        elif self.suit < other.suit: return False
        elif self.rank > other.rank: return True
        else: return False

class CardCollection(list):
    def __init__(self, args=[], avalues=[], face_up=False, size=0):
        list.__init__(self, args)  #only "args" works as parameter. Why?
        self.face_up = face_up
        self.size = size
        self.avalues = avalues
    def deal(self, number, deck):
        for i in range(number):
            self.append(deck[0])
            try: deck.pop(0)
            except IndexError: raise(IndexError("Deck empty!"))
    def __str__(self):
        s = "["
        for c in self:
            s += str(c) + ", "
        s += "]"
        return s
    def clear(self):
        del self[:]
        self.avalues.clear()
        self.size = 0


class Player:
    def __init__(self, name=None):
        self.name = name
    def chooseCard(self, game):
        ...

class RandomPlayer(Player):
    def chooseCard(self, game):
        legalCards = game.get_moves(self.name)
        return legalCards[randint(0,len(legalCards)-1)]

class MCPlayer1(Player):
    def chooseCard(self, game):
        legalCards = game.get_moves(self.name)
        hand = game.playerpiles[game.names.index(self.name)][0] #give the player the correct hand from playerpiles list
        rootnode = Node(state=game)
        for i in range(ITERMAX):
            node = rootnode
            state = game.clone()
            
            #Select
            while node.untriedMoves == [] and node.childNodes != []:
                node = node.UCTSelectChild()
                state.move = node.move
                state.play()
            #Expand
            if node.untriedMoves != []:
                m = choice(node.untriedMoves)
                state.move = m
                state.play()
                node = node.addChild(m, state)
            #Rollout - GetRandomMove function?
            while state.get_moves(self.name) != []: #TODO figure this one out (+name issue!)!!
                state.move = choice(state.get_moves(self.name))
                state.play()
            #Backpropagation
            while node != None:
                node.Update((-state.score(node.turn)))
                node = node.parentNode
            
        # Output some information about the tree - can be omitted
        if (VERBOSE): print(rootnode.TreeToString(0))
        else: print(rootnode.ChildrenToString())

        return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move  # return the move that was most visited

class MCPlayer2(Player):
    def chooseCard(self, game):
        legalCards = game.get_moves(self.name)
        hand = game.playerpiles[game.names.index(self.name)][0] #give the player the correct hand from playerpiles list TODO: delete?

class MCHelpPlayer(Player):
    def chooseCard(self, game):
        legalCards = game.get_moves(self.name)
        return legalCards[randint(0,len(legalCards)-1)]

class HumanPlayer(Player):
    def chooseCard(self, game):
        legalCards = game.findLegal(self.name)
        # +++ Begin choosing +++
        hand = game.playerpiles[game.names.index(self.name)][0] #give the player the correct hand from playerpiles list
        hand.sort()
        print("+++ Your turn:")
        print("Already played: ", game.generalpiles[0])
        for i in range(len(hand)):
            print(i,":",hand[i],("*" if (hand[i] in legalCards) else ""))
        while True:
             inp = input("Choose card index: ")
             try: inp = int(inp)
             except: continue
             if inp<len(hand) and (hand[inp] in legalCards): break
        # +++ end choosing +++
        return hand[inp]

SDECK = [Card(i,j) for j in range(4) for i in range(13)]

class Game:
    """
        Game object which describes a the state of a game
    """
    def __init__(self, players, deck, score, playerpiles=[], generalpiles=[], markers=[]):
        self.players = players
        self.names = list(range(4))
        for i in range(len(self.players)):
            self.players[i].name = self.names[i]
        self.num_players = len(players)
        self.deck = deck
        self.score = score
        self.playerpiles = []
        self.generalpiles = []
        self.markers = markers  #misc indicators
        self.turn = 0
        self.move = None #chosen move (also for hypothetical test situations)

        for i in range(len(players)):
            self.playerpiles.append([])
            for j in playerpiles:
                c = CardCollection()
                c.deal(j, self.deck)
                self.playerpiles[i].append(c)
        for i in generalpiles:
            c = CardCollection()
            c.deal(i, self.deck)
            self.generalpiles.append(c)
        for i in range(len(players)): players[i].name = i
    def next(self, player):
        return (player+1)%self.num_players
    def clone(self): #clone Game instance
        cl = Game([RandomPlayer(),RandomPlayer(),RandomPlayer(),RandomPlayer()], self.deck, self.score)
        cl.playerpiles = self.playerpiles[:] #shallow copy because state will change in clone 
        cl.generalpiles = self.generalpiles[:]
        cl.markers = self.markers[:]
        cl.play = self.play
        cl.score = self.score
        return cl

# Node class based on eponymous class in UTC.py by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.turn = state.turn #Player who's turn it is. The only part of the state that the Node needs later
        self.untriedMoves = state.get_moves(self.turn) # future child nodes
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s
