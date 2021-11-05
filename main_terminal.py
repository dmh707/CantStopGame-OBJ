'''
Project Name: Can't Stop
Author: Dawn Harper
Copyright: October 2021
Description:
This is a test version of my larger project to build the board game "Can't Stop" in Python.
This version of the game is fully functional, but was built for my testing purposes and is 
more difficult to use.
I'm including this file to show that the back end of the game, "game_classes" can be attached to 
different UI's effectively
'''

from game_classes import Board
'''
1. get roll, sums, and number of cols with white pieces
2. w.chooseSums()
3. run the rest of the round
4. w.rollAgainBool()
5. repeat or
6. end the turn
'''
class Terminal_game:
    def __init__(self) -> None:
        self.board = Board(self.getPlayerList())
        self.play()
    def getPlayerList(self):
        playersList = input('submit comma separated list of players:').split(',')
        return playersList
    def play(self):
        while True:
            player = self.board.activePlayer.name
            print(f'It is {player}\'s turn')
            if self.board.applySums(self.chooseSums()):
                semiCompletedCols=self.board.getWhitePieceCompletedCols()
                if semiCompletedCols:
                    for col in semiCompletedCols:
                        print(f'Your white piece has reached the end of column {col}.')
                if self.board.whitePiecesLeft()==0:
                    if self.rollAgainBool():
                        continue
                else:
                    continue
            else:
                print(f'Oh no, {player}! You have bombed! Your progress from this turn is lost.')
            self.board.stopTurn()
            if self.board.didActivePlayerWin():
                print(f'{self.board.activePlayer.name} Won!!')
                break
            self.board.nextActivePlayer()

            if input('quit? (return any letter for yes, return nothing for no)') != '':
                break
    def rollAgainBool(self):
        if input('Do you want to roll again? (return any letter for yes, return nothing for no)') == '':
            return False
        return True
    def chooseSums(self):
        dice = self.board.dice.roll()
        sums = self.board.filterSums()
        if not sums:
            return False
        whitePieces = list(self.board.colsWithWhitePieces.keys())
        whitePieces.sort()
        print(f"You have rolled: {dice}")
        print(f"Your sums are: {sums}")
        progress = self.board.getActivePlayerProgress()
        if progress:
            print(f'Your markers are on the following spaces: ')
            for num,col in progress.items():
                print(f'{num}:{col}')
        if len(whitePieces)>0:
            print(f'Your white pieces are in the following columns: {whitePieces}')
        newWhitePieces =[]
        selectedSums = self.selectOption(sums, 'columns')
        for sum  in selectedSums:
            if sum not in whitePieces:
                newWhitePieces.append(sum)
        if len(newWhitePieces)>self.board.whitePiecesLeft():
            if newWhitePieces[0] != newWhitePieces[1]:
                for sum in newWhitePieces:
                    selectedSums.remove(sum)
                if self.board.whitePiecesLeft() != 0:
                    print('You only have one free white piece left. Which column would you like to play on?')
                    x = self.selectOption(newWhitePieces)
                    selectedSums.append(x)
                    selectedSums.sort()
        print(selectedSums)
        if len(selectedSums)==0:
            selectedSums=False
        return selectedSums

    def selectOption(self,lyst,nameOfThing="option"):
        print(f'Select the index number of your chosen {nameOfThing}: ')
        for i in range(len(lyst)):
            print(f'Index {i}: {lyst[i]}')
        while True:
            x = input(f'input the index number of your chosen {nameOfThing}: ')
            try:
                return lyst[int(x)]
            except:
                nums = ''
                for i in range(len(lyst)):
                    nums +=f"{i}, "
                nums = nums[:-2]
                print(f'That selection is invalid. Please enter one of the following integers: {nums}')

def main():
    game = Terminal_game()
if __name__ == "__main__":
    main()