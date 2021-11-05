'''
Project Name: Can't Stop
Author: Dawn Harper
Copyright: October 2021
Description:

This a Python version of the board game "Can't Stop."
You can find the rules to the game here: https://www.ultraboardgames.com/cant-stop/game-rules.php

I made this game for fun and to practice the python principles I was learning in school: 
abstract classes and functions, loose coupling (I built two UI's that work with 
the same back end interchangeably, although the front ends would not work instantly with 
a different back end), and building GUIs (through BreezyPythonGui).

In future, I hope to improve the game in the following ways:
-add documentation to this file, like those found in game_classes
-add images to make the experience more visually intuitive
-add a visual tutorial for the game
-make it easier to see the current user's progress
'''
from breezypythongui import EasyFrame,EasyDialog,EasyRadiobuttonGroup
from game_classes import Board,Col,Marker,Player
import abc
class GameWindow(EasyFrame):
    def __init__(self,test=False):
        super().__init__(title="Can't Stop Game", width=1000, height=500, resizable=True)
        self.currentWindow = False
        self.board = False
        self.test = test
        self.start()
    def start(self):
        self.startgame = StartGame(self)
    def clear_frame(self):
        for widgets in self.winfo_children():
            widgets.destroy()
class SubGame(abc.ABC):
    def __init__(self,parent):
        assert isinstance(parent,GameWindow)
        self.parent = parent
        self.start()
    @abc.abstractmethod
    def start(self):
        pass
class StartGame(SubGame):
    def __init__(self,parent):
        super().__init__(parent)
    def start(self):
        if self.parent.test:
            self.startBtnFunc()
            return
        self.parent.clear_frame()
        self.parent.addButton(text='Start',row=0,column=0,command=self.startBtnFunc)
    def startBtnFunc(self):
        self.parent.clear_frame()
        self.parent.currentWindow = GetPlayersList(self.parent)
class GetPlayersList(SubGame):
    def __init__(self, parent):
        super().__init__(parent)
    def start(self):
        if self.parent.test:
            self.parent.board = Board(['Cptn Picard','Lt Worf'],True)
            self.parent.currentWindow=MainGame(self.parent)
            return
        self.parent.addLabel('Who is playing this game? Please write each player\'s name on a separate line.',row=0,column=0)
        self.txtPlayerList=self.parent.addTextArea(text='',row=1,column=0)
        self.parent.addButton(text='submit names',row=2,column=0,command=self.submit)
    def submit(self):
        self.parent.board = Board(self.txtPlayerList.getText().split('\n')[:-1])
        self.parent.clear_frame()
        self.parent.currentWindow=MainGame(self.parent)
class MainGame(SubGame):
    def __init__(self, parent):
        self.canStop = False
        super().__init__(parent)
    def start(self):
        assert isinstance(self.parent.board,Board)
        playerNames='Players: \n'
        for i in range(len(self.parent.board.playerStrList)):
            name = self.parent.board.playerStrList[i]
            if name == self.parent.board.activePlayer.name:
                playerNames+=f'* {i}. {name}\n'
                continue
            playerNames+=f'{i}. {name}\n'
        playerNames+='\n* indicates the current active player'
        self.btnsList = []
        self.lblActivePlayer=self.parent.addLabel(text=f'It is {self.parent.board.activePlayer.name}\'s turn.',row=0,column=0)
        self.panelBoard=self.parent.addPanel(row=1,column=0)
        self.setBoard()
        self.panelDice=self.parent.addPanel(row=2,column=0)
        self.lblPanelDice=self.panelDice.addLabel(text=f'{self.parent.board.activePlayer.name}\'s Dice Roll: ',row=0,column=0,columnspan=4)
        self.lblDice=[False]*4
        for i in range(4):
            self.lblDice[i]=self.panelDice.addLabel(text=' ',row=1,column=i)
        self.panelBtns=self.parent.addPanel(row=3,column=0)
        if self.canStop:
            self.btnNext=self.panelBtns.addButton(text='STOP',row=0,column=1,command=self.next)
            self.btnsList.append(self.btnNext)
        self.btnRoll=self.panelBtns.addButton(text='roll',row=0,column=0,command=self.roll)
        self.btnsList.append(self.btnRoll)
        self.lblPlayerNames=self.parent.addLabel(text=playerNames,row=0,column=1,rowspan=2,sticky='NE')
        self.btnInstructions=self.parent.addButton(text='INSTRUCTIONS',row=4,column=0,command=self.instructionFunc)
    def instructionFunc(self):
        instructions = 'You will place 3 \'WHITE PIECE\' markers on the board during your turn, each on a separate column. Each time you roll the number of a column which houses one of your white pieces, you advance 1 space. \n\nThe GOAL is to advance to the end of 3 columns before any other player. \n\nIf at any point, you cannot play on your roll, you lose your progress for that turn. This is called \'BOMBING\'. If at any point after placing all 3 white pieces, you chose to STOP, your current progress will be saved, and you may place white pieces where you left off on your next turn. This is indicated by your index number on the board. \n\nOnce a COLUMN has been COMPLETED by one player, no one may play that column. This means you may sometimes roll only numbers from columns that are completed and cannot be played, and therefore you may bomb without having placed every white piece. \n\nThems the breaks. \n\nThe most common numbers to roll have the longest columns. \n\nBest of Luck.'
        self.parent.messageBox(title='Instructions',message=instructions,width=100,height=30)
    def next(self):
        assert isinstance(self.parent.board,Board)
        self.parent.board.stopTurn()
        if self.parent.board.didActivePlayerWin():
            self.parent.currentWindow=Winstate(self.parent,self)
            return
        self.parent.board.nextActivePlayer()
        self.parent.clear_frame()
        self.canStop=False
        self.start()
    def roll(self):
        assert isinstance(self.parent.board,Board)
        dice = self.parent.board.dice.roll()
        sums=self.parent.board.filterSums()
        if not sums:
            #bomb
            self.parent.messageBox(title='Oops! You\'ve bombed!',message=f'Oops! You cannot use any of the sums from these dice. Your turn is over and your progress from this turn is lost.')
            self.endChooseSum(sums)
            return
        for i in range(len(dice)):
            self.lblDice[i]['text']=str(dice[i])
        self.btnSums = [False]*len(sums)
        self.selectOption(sums,self.chooseSum)
    def chooseSum(self,sums):
        def func():
            whitePieces = list(self.parent.board.colsWithWhitePieces.keys())
            whitePieces.sort()
            selectedSums = sums
            newWhitePieces =[]
            for sum in selectedSums:
                if sum not in whitePieces:
                    newWhitePieces.append(sum)
            #if I'm trying to place too many new white pieces
            #could be 2:1(same int twice)-do nothing,2:1(different ints)-choose one,2:0-remove, or 1:0-remove
            if len(newWhitePieces)>self.parent.board.whitePiecesLeft():
                #if the first and second white pieces are different
                ##handle if there is only one new white piece
                if self.parent.board.whitePiecesLeft()==0 or newWhitePieces[0] != newWhitePieces[1]:
                    #remove all newWhitePieces from selected sums
                    for sum in newWhitePieces:
                        selectedSums.remove(sum)
                    #if there is only one white piece left (and there are two different new white pieces)
                    if self.parent.board.whitePiecesLeft()==1:
                        #allow the user to select one
                        self.selectOption(newWhitePieces,self.btnApplyASelectedSum)
                        return
            self.endChooseSum(selectedSums)
        return func
    def btnApplyASelectedSum(self,sum):
        def func():
            x=sum
            if not isinstance(sum,list):
                x = [sum]
            self.endChooseSum(x)
        return func 
    def endChooseSum(self,selectedSums):
        if not selectedSums or len(selectedSums)==0:
            selectedSums=False
        
        self.afterSums(self.parent.board.applySums(selectedSums))  
    def selectOption(self,options,func):
        self.clear_btns()
        assert isinstance(options,list)
        self.btnSums=[False]*len(options)
        for i in range(len(options)):
            x=self.btnSums[i]=self.panelBtns.addButton(text=str(options[i]),row=1,column=i,command=func(options[i]))
            self.btnsList.append(x)
    def afterSums(self,sums):
        if sums:
            if self.parent.board.whitePiecesLeft()==0:
                self.canStop = True
            else:
                self.canStop = False
        else:
            self.next()
            return
            #print(f'Oh no, {self.parent.board.activePlayer.name}! You have bombed! Your progress from this turn is lost.')
        self.start()
        #self.next()
    def clear_btns(self):
        for btn in self.btnsList:
            btn.destroy()
    def setBoard(self):
        board = self.parent.board
        assert isinstance(board,Board)
        for col in board.cols.values():
            assert isinstance(col,Col)
            markers = self.getMarkersBySpace(col)
            for space in col.spaces.values():
                txt='.'
                if space.isFinal:
                    txt = str(col.name)
                if markers and space.name in markers:
                    playerNums = []
                    for x in markers[space.name]:
                        assert isinstance(x,Marker)
                        name = x.player.name
                        i = self.parent.board.playerStrList.index(name)
                        playerNums.append(str(i))
                    playerNums.sort()
                    txt=','.join(playerNums)
                if col.whitePiece and col.whitePiece.space == space:
                    txt = 'W'
                if col.donePlayer:
                    txt=' '
                    if space.isFinal:
                        txt = col.donePlayer.name[:5]
                self.panelBoard.addLabel(text=txt,row=space.name,column=col.name)
    def getMarkersBySpace(self,col):
        markers = {}
        if len(col.markers)==0:
            return False
        for marker in col.markers:
            if marker.space.name in markers:
                markers[marker.space.name].append(marker)
            else:
                markers[marker.space.name]=[marker]
        return markers
class Winstate(SubGame):
    def __init__(self, parent,mainGame):
        self.mainGame = mainGame
        super().__init__(parent)
    def start(self):
        assert isinstance(self.parent.board,Board)
        self.parent.clear_frame()
        playerNames=''
        for i in range(len(self.parent.board.playerStrList)):
            name = self.parent.board.playerStrList[i]
            if name == self.parent.board.activePlayer.name:
                playerNames+=f'* {i}. {name}\n'
                continue
            playerNames+=f'{i}. {name}\n'
        self.btnsList = []
        self.lblActivePlayer=self.parent.addLabel(text=f'{self.parent.board.activePlayer.name} has won!!!',row=0,column=0)
        self.lblActivePlayer2=self.parent.addLabel(text=f'{self.parent.board.activePlayer.name} has won!!!',row=3,column=0)
        self.mainGame.panelBoard=self.parent.addPanel(row=1,column=0)
        self.mainGame.setBoard()
        self.lblPlayerNames=self.parent.addLabel(text=playerNames,row=0,column=1,rowspan=2,sticky='NE')
        

def main():
    '''game = GuiGame()
    game.mainloop()'''
    GameWindow().mainloop()
if __name__ == "__main__":
    main()