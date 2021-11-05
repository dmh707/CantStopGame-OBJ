'''
Project Name: Can't Stop
Author: Dawn Harper
Copyright: October 2021
Description:

This is the back end file for my Python version of Can't Stop. This file runs all parts of the game 
that are not requesting and accepting and understanding user input.

'''

from random import randint
            
class Board:
    '''
    Runs a Can't Stop game.
    '''
    def __init__(self,playerStrList,test=False) -> None:
        assert isinstance(playerStrList,list)
        assert isinstance(playerStrList[0],str)
        self.test = test
        self.playerStrList = playerStrList
        self.players = []
        self.activePlayer = False
        self.colsWithWhitePieces = {}
        self.maxWhitePieces = 3
        self.cols = {}
        self.colsToWin = 3
        if self.test:
            self.colsToWin=2
        self.setup(playerStrList)
        self.dice = Dice()
    def __str__(self) -> str:
        return f"<Board Obj>\nactivePlayer = {self.activePlayer}\ncols = {self.cols}\ncolsWithWhitePieces = {self.colsWithWhitePieces}"
    def didActivePlayerWin(self):
        '''
        returns True if active player won, and False otherwise
        '''
        assert isinstance(self.activePlayer,Player)
        if len(self.activePlayer.doneCols)>=self.colsToWin:
            return True
        return False
    def getWhitePieceCompletedCols(self):
        '''
        returns a list of the names(int) of cols that have a white piece which has completed the column
        '''
        cols = []
        for col in self.colsWithWhitePieces.values():
            assert isinstance(col,Col)
            if col.whitePiece.space.isFinal:
                cols.append(col.name)
        if len(cols)==0:
            return False
        return cols
    def getActivePlayerProgress(self):
        '''
        returns a dictionary with the progress info for the active player. 
        format: {col.name : {'progress':distance progressed, 'outOf':number of spaces, 'isFinal':boolean of whether the col is complete}}
        '''
        assert isinstance(self.activePlayer,Player)
        progress = {}
        for col in self.cols.values():
            assert isinstance(col,Col)
            marker = col.getMarkerByPlayer(self.activePlayer)
            if marker:
                assert isinstance(marker,Marker)
                progress[col.name]={
                    'progress':marker.space.name,
                    'outOf':len(col.spaces),
                    'isFinal':marker.space.isFinal}
        if len(progress)==0:
            return False
        return progress
    def setup(self,playersStrList):
        '''
        This function is only used by Board itself. Do not call from outside.
        It sets up the Players and Columns so the game can play.
        '''
        for player in playersStrList:
            self.players.append(Player(player))
        self.activePlayer = self.players[0]
        self.setCols()
    def setCols(self):
        '''
        This function is only used by Board itself. Do not call from outside.
        It sets up the Columns and Spaces.
        '''
        first_col=2
        last_col=12
        mid_col=7
        add_by=2
        start=3
        if self.test:
            add_by=0
            start=2
        counter = start
        for x in range(first_col,mid_col+1):
            self.cols[x]=Col(x,counter)
            counter+=add_by
        for x in range(mid_col,last_col+1):
            counter-=add_by
            self.cols[x]=Col(x,counter)
    def nextActivePlayer(self):
        '''
        sets self.activePlayer to the next player in the list.
        '''
        if self.activePlayer:
            i = self.players.index(self.activePlayer)
            j = (i+1) % len(self.players)
            self.activePlayer = self.players[j]
    def whitePiecesLeft(self):
        '''
        returns the number of white pieces that have not been placed yet
        '''
        x=self.maxWhitePieces - len(self.colsWithWhitePieces)
        if x <0:
            x=0
        return x
    def applySums(self,chosenSums):
        '''
        chosenSums is a list of integers or False (bool). 
        If False, self.bomb() is called and the function returns False.
        Otherwise, the numbers in the list will have white pieces set(if necessary) and iterated by 1, and the function returns True.
        '''
        if not chosenSums:
            self.bomb()
            return False
        self.setWhitePieces(chosenSums)
        return True
    def filterSums(self):
        '''
        returns a list of any integers from self.sums which are playable. 
        if no sums are playable, returns False.
        '''
        playableCols = self.getPlayableCols()
        sums = self.dice.sums
        new_sums=[]
        for x in sums:
            new_x=[]
            for y in x:
                if y in playableCols.keys():
                    new_x.append(y)
            if len(new_x) != 0:
                new_sums.append(new_x)
        if len(new_sums) == 0:
            return False
        return new_sums
    def getPlayableCols(self):
        '''
        returns a dictionary of columns that are playable (not completed).
        if there are no spare white pieces, returns only cols with white pieces.
        '''
        playable = {}
        if len(self.colsWithWhitePieces)>=self.maxWhitePieces:
            return self.colsWithWhitePieces
        for col in self.cols.values():
            assert isinstance(col,Col)
            if not col.donePlayer:
                playable[col.name]=col
        return playable
    def setWhitePieces(self,chosenSums):
        '''
        chosenSums is a list of integers(one or two). 
        sets (if necessary) and iterates a white piece for each sum
        '''
        if len(chosenSums)==2 and chosenSums[0]==chosenSums[1]:
            self.setWhitePieces([chosenSums[0]])
            chosenSums.pop(0)
        for sum in chosenSums:
            if sum in self.colsWithWhitePieces.keys():
                x = self.colsWithWhitePieces[sum]
                assert isinstance(x,Col)
                x.iterateWhitePieceByOne()
            else:
                x=self.cols[sum]
                assert isinstance(x,Col)
                x.setWhitePiece(self.activePlayer)
                self.colsWithWhitePieces[sum] = self.cols[sum]
    def bomb(self):
        '''
        clears out all white pieces from cols and clears self.colsWithWhitePieces.  
        to be called when a player has bombed
        '''
        for col in self.colsWithWhitePieces.values():
            assert isinstance(col,Col)
            col.whitePiece = False
        self.colsWithWhitePieces={}
    def stopTurn(self):
        '''
        updates the markers for each white piece and clears out white pieces and colsWithWhitePieces.  
        to be called when the player ends their turn on purpose
        '''
        for col in self.colsWithWhitePieces.values():
            assert isinstance(col,Col)
            if col.whitePiece:
                col.setMarker()
                col.whitePiece=False
        self.colsWithWhitePieces={}
class Player:
    '''
    contains a player
    '''
    def __init__(self,name) -> None:
        self.name=name
        self.doneCols=[]
    def __str__(self) -> str:
        return '<Player obj>' + self.name
    def updateDoneCols(self,col):
        '''
        col is a Col object.  
        adds col to self.doneCols.  
        to be called when a player has ended a turn after completing a column
        '''
        if col not in self.doneCols:
            self.doneCols.append(col)
class Col:
    '''
    contains a single column
    '''
    def __init__(self,name,length) -> None:
        assert isinstance(name,int)
        assert isinstance(length,int)

        self.name = name
        self.spaces = {}
        self.markers = []
        self.whitePiece = False
        self.donePlayer = False
        for x in range(length):
            self.spaces[x]=Space(x)
        self.spaces[length]=Space(length,True)
    def __str__(self) -> str:
        output=f"<Col obj>\nname = {self.name}\nspaces = {self.spaces}"
        if len(self.markers) > 0:
            output+=f"\nmarkers = {self.markers}"
        if self.whitePiece:
            output+=f"\nwhitePiece = {self.whitePiece}"
        if self.donePlayer:
            output+=f"\ndonePlayer = {self.donePlayer}"
        return output
    def setMarker(self):
        '''
        sets a or updates a player's marker to the space of the current white piece.
        returns the player's marker
        '''
        if self.whitePiece:
            assert isinstance(self.whitePiece,WhitePiece)
            player = self.whitePiece.player
            marker = self.getMarkerByPlayer(player)
            if marker:
                marker.updateSpace(self.whitePiece.space)
            else:
                self.markers.append(Marker(player,self.whitePiece.space))
                marker = self.markers[-1]
            if marker.space.isFinal:
                self.done()
            return marker
    def getMarkerByPlayer(self,player):
        '''
        player is a Player object.
        returns the marker of the player object.
        if no marker, returns false.
        '''
        for x in self.markers:
            assert isinstance(x,Marker)
            if player is x.player:
                return x
        return False
    def done(self):
        '''
        only to be called by a Col object
        if a player has completed a column and ended the turn, this updates the col's donePlayer and the players doneCols.
        '''
        assert isinstance(self.whitePiece,WhitePiece)
        self.donePlayer = self.whitePiece.player
        self.donePlayer.updateDoneCols(self)
    def iterateWhitePieceByOne(self):
        '''
        moves the Col's whitePiece up one Space, unless there are no more Spaces
        '''
        assert isinstance(self.whitePiece,WhitePiece)
        if self.whitePiece.space.isFinal:
            return
        nextSpaceName = self.whitePiece.space.name + 1
        self.whitePiece.space = self.spaces[nextSpaceName]
        assert isinstance(self.whitePiece.space,Space)
    def setWhitePiece(self,player):
        '''
        player is a Player object. 
        sets a white piece for this column and player either ahead of their current 
        marker or at the start of the column.
        '''
        marker = self.getMarkerByPlayer(player)
        if not marker:
            self.whitePiece = WhitePiece(player,self.spaces[0])
        else:
            self.whitePiece = WhitePiece(player,marker.space)
            self.iterateWhitePieceByOne()
class Marker:
    '''
    contains a player's marker in a Col
    '''
    def __init__(self,player,space) -> None:
        assert isinstance(player,Player)
        assert isinstance(space,Space)
        self.objType = 'Marker'
        self.player = player
        self.space = space
    def __str__(self) -> str:
        output = f"<{self.objType} obj>\nplayer = {self.player}\nspace = {self.space}"
        if self.space.isFinal:
            output+=f"\nisFinal"
        return output
    def updateSpace(self,space):
        '''
        space is a Space object. 
        sets self.space to space, as long as we aren't moving backwards
        '''
        assert isinstance(space,Space)
        if space.name<self.space.name:
            print('handle: new space is not ahead of old space')
            return
        self.space = space
class WhitePiece(Marker):
    '''
    contains a player's white piece in a col
    '''
    def __init__(self, player, space) -> None:
        super().__init__(player, space)
class Space:
    '''
    contains a space within a col
    '''
    def __init__(self,name,isFinal=False) -> None:
        self.name = name
        self.isFinal = isFinal
    def __str__(self) -> str:
        return '<Space obj>: ' +str(self.name) + ' ' + str(self.isFinal)      
class Dice:
    '''
    contains 4 dice and their pairs of sums
    '''
    def __init__(self) -> None:
        self.dice = []
        self.sums = []
        self.roll()
    def roll(self):
        '''
        sets the self.dice and self.sums. 
        returns the list of dice.
        dice rolls are random D6 rolls. there are 4 dice.
        sums are all possible ways to split 4 dice into two sums of two dice each.
        '''
        self.dice = []
        for x in range(0,4):
            i = randint(1,6)
            self.dice.append(i)
        self.dice.sort()
        self.setSums()
        return self.dice
    def setSums(self):

        '''
        only to be called by self.roll()
        sets and returns the self.sums based on the dice
        '''
        wholeSum = 0
        for x in self.dice:
            wholeSum+=x
        self.sums=[]
        a=self.dice[0]
        for x in range(1,4):
            b=self.dice[x]
            sum1=a+b
            sum2 = wholeSum-sum1
            sumset = [sum1,sum2]
            sumset.sort()
            if sumset not in self.sums:
                self.sums.append(sumset)
        self.sums.sort()
        return self.sums