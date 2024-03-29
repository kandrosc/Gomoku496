"""
simple_board.py

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""

import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
                       PASS, is_black_white, coord_to_point, where1d, MAXSIZE

class SimpleGoBoard(object):
    # Initialize the previous player to black
    
    
    def get_color(self, point):
        return self.board[point]
    
    def display():
        return;

    def pt(self, row, col):
        return coord_to_point(row, col, self.size)
    
    def setNext(self,colour):
        self.next_color=colour
    
    def getSize(self):
        return self.size
    
    def setStore(self,store):
        self.store=store

    def is_legal(self, point, color):
        """
        Check whether it is legal for color to play on point
        """
        board_copy = self.copy()
        # Try to play the move on a temporary copy of board
        # This prevents the board from being messed up by the move
        
        
        legal = board_copy.play_move(point, color)
        return legal

    def get_empty_points(self):
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def __init__(self, size):
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
       
        self.reset(size)

    def reset(self, size):
        """
        Creates a start state, an empty board with the given size
        The board is stored as a one-dimensional array
        See GoBoardUtil.coord_to_point for explanations of the array encoding
        """
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.ko_recapture = None
        self.current_player = BLACK
        self.maxpoint = size * size + 3 * (size + 1)
        self.board = np.full(self.maxpoint, BORDER, dtype = np.int32)
        self._initialize_empty_points(self.board)
        # 3 new variables:  lists that store the integer coordinates of every white and black piece currently on the board
        # a list to keep track of which points have been checked while checking for a win
        
        # 1st list: storage
        # 2nd list: black pieces
        # 3rd list: white pieces
        self.store=[[],[],[]]
        

    def copy(self):
        b = SimpleGoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.ko_recapture = self.ko_recapture
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        b.setStore(self.store)
        return b

    def row_start(self, row):
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1
        
    def _initialize_empty_points(self, board):
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start = self.row_start(row)
            board[start : start + self.size] = EMPTY

    def is_eye(self, point, color):
        """
        Check if point is a simple eye for color
        """
        if not self._is_surrounded(point, color):
            return False
        # Eye-like shape. Check diagonals to detect false eye
        opp_color = GoBoardUtil.opponent(color)
        false_count = 0
        at_edge = 0
        for d in self._diag_neighbors(point):
            if self.board[d] == BORDER:
                at_edge = 1
            elif self.board[d] == opp_color:
                false_count += 1
        return false_count <= 1 - at_edge # 0 at edge, 1 in center
    
    def _is_surrounded(self, point, color):
        """
        check whether empty point is surrounded by stones of color.
        """
        for nb in self._neighbors(point):
            nb_color = self.board[nb]
            if nb_color != BORDER and nb_color != color:
                return False
        return True

    def _has_liberty(self, block):
        """
        Check if the given block has any liberty.
        block is a numpy boolean array
        """
        for stone in where1d(block):
            empty_nbs = self.neighbors_of_color(stone, EMPTY)
            if empty_nbs:
                return True
        return False

    def _block_of(self, stone):
        """
        Find the block of given stone
        Returns a board of boolean markers which are set for
        all the points in the block 
        """
        marker = np.full(self.maxpoint, False, dtype = bool)
        pointstack = [stone]
        color = self.get_color(stone)
        assert is_black_white(color)
        marker[stone] = True
        while pointstack:
            p = pointstack.pop()
            neighbors = self.neighbors_of_color(p, color)
            for nb in neighbors:
                if not marker[nb]:
                    marker[nb] = True
                    pointstack.append(nb)
        return marker

    def _detect_and_process_capture(self, nb_point):
        """
        Check whether opponent block on nb_point is captured.
        If yes, remove the stones.
        Returns True iff only a single tone was captured.
        This is used in play_move to check for possible ko
        """
        single_capture = None 
        opp_block = self._block_of(nb_point)
        if not self._has_liberty(opp_block):
            captures = list(where1d(opp_block))
            self.board[captures] = EMPTY
            if len(captures) == 1:
                single_capture = nb_point
        return single_capture
    
    def board_state(self):
        return

    def play_move(self, point, color):
        """
        Play a move of color on point
        Returns boolean: whether move was legal
        """

        # Ensures players can't play after someone already won
        if (self.checkWin(WHITE) or self.checkWin(BLACK) or self.get_empty_points().size==0):
            
            return False

        else:
      
            # Ensure the expected player is playing
                
            try:
                # Ensure the player is playing on an empty spot
                if self.board[point] != EMPTY:
                    return False
                self.board[point] = color
                

                self.store[color].append(point)
                self.store[color].sort()
                return True

            except ValueError:
                print("Board is full, random move cannot be generated")
                return False


    def neighbors_of_color(self, point, color):
        """ List of neighbors of point of given color """
        nbc = []
        for nb in self._neighbors(point):
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc
        
    def _neighbors(self, point):
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point):
        """ List of all four diagonal neighbors of point """
        return [point - self.NS - 1, 
                point - self.NS + 1, 
                point + self.NS - 1, 
                point + self.NS + 1]
    
    
    
    # function that returns all checked points back to their respective lists
    def checkout(self,colour):
        for i in self.store[0]:
            self.store[colour].append(i)
        self.store[colour].sort()
        self.store[0]=[]
    
    # function for checking whether or not a win has happened horizontally
    def checkH(self,point,colour,chain):
        if chain>1:
            if self.board[point+1]==colour:
                self.store[0].append(point+1)
                self.store[colour].remove(point+1)
                r=self.checkH(point+1,colour,chain-1)
                return r
            else:
                return False
        else:
            return True
    
    def checkV(self,point,colour,chain):
        if chain>1:
            if self.board[point+self.NS]==colour:
                self.store[0].append(point+self.NS)
                self.store[colour].remove(point+self.NS)
                r=self.checkV(point+self.NS,colour,chain-1)
                return r
            else:
                return False
        else:
            return True
    
    def checkDR(self,point,colour,chain):
        if chain>1:
            if self.board[point+self.NS + 1]==colour:
                self.store[0].append(point+self.NS + 1)
                self.store[colour].remove(point+self.NS + 1)
                r=self.checkDR(point+self.NS + 1,colour,chain-1)
                return r
            else:
                return False
        else:
            return True
    
    def checkDL(self,point,colour,chain):
        if chain>1:
            if self.board[point+self.NS - 1]==colour:
                self.store[0].append(point+self.NS - 1)
                self.store[colour].remove(point+self.NS - 1)
                r=self.checkDL(point+self.NS - 1,colour,chain-1)
                return r
            else:
                return False
        else:
            return True       
    
    
    
    def checkWin(self,colour):
        # check horizontal
        win=False
        for i in self.store[colour]:
            win=self.checkH(i,colour,5)
            if win:
                self.checkout(colour)
                break            
        if not win:
            self.checkout(colour)
            for i in self.store[colour]:
                # check vertical
                win=self.checkV(i,colour,5)
                if win:
                    self.checkout(colour)
                    break
            if not win:
                self.checkout(colour)
                for i in self.store[colour]:
                    # check diagonal \
                    win=self.checkDR(i,colour,5)
                    if win:
                        self.checkout(colour)
                        break                    
                if not win:
                    self.checkout(colour)
                    for i in self.store[colour]:
                        # check diagonal /
                        win=self.checkDL(i,colour,5)
                        if win:
                            self.checkout(colour)
                            break                        
                    if not win:
                        self.checkout(colour)
                        return False
                    return True
                return True
            return True
        return True
    
    
    
    # This function will determine which state the board is in, whether white or black won, draw, or unknown
    def checkState(self):
        if self.checkWin(WHITE):
            return WHITE
        elif self.checkWin(BLACK):
            return BLACK
        elif self.get_empty_points().size==0:
            return PASS
        return -1
