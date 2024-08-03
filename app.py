import streamlit as st
import random
import pandas as pd
import re

class Board:
    def __init__(self, dim_size, num_bombs):
        self.dim_size = dim_size
        self.num_bombs = num_bombs
        self.board = self.make_new_board()
        self.dug = set()

    def make_new_board(self):
        board = [[0 for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            row = random.randint(0, self.dim_size - 1)
            col = random.randint(0, self.dim_size - 1)
            if board[row][col] == '*':
                continue
            board[row][col] = '*'
            bombs_planted += 1
            for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
                for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                    if board[r][c] != '*':
                        board[r][c] += 1
        return board

    def get_num_neighboring_bombs(self, row, col):
        num_neighboring_bombs = 0
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if r == row and c == col:
                    continue
                if self.board[r][c] == '*':
                    num_neighboring_bombs += 1
        return num_neighboring_bombs

    def dig(self, row, col):
        self.dug.add((row, col))
        if self.board[row][col] == '*':
            return False
        elif self.board[row][col] > 0:
            return True
        for r in range(max(0, row-1), min(self.dim_size-1, row+1)+1):
            for c in range(max(0, col-1), min(self.dim_size-1, col+1)+1):
                if (r, c) in self.dug:
                    continue
                self.dig(r, c)
        return True

    def to_dataframe(self):
        visible_board = [[' ' for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        for row in range(self.dim_size):
            for col in range(self.dim_size):
                if (row, col) in self.dug:
                    visible_board[row][col] = str(self.board[row][col])
                else:
                    visible_board[row][col] = ' '
        return pd.DataFrame(visible_board)

def main():
    # Set page configuration
    st.set_page_config(page_title="Minesweeper",
                       layout="wide",
                       page_icon="👾")
    
    st.title("Minesweeper")

    # Sidebar for settings
    dim_size = st.sidebar.slider("Board Size", 5, 20, 10)
    num_bombs = st.sidebar.slider("Number of Bombs", 1, 100, 10)

    # Initialize the game board
    if 'board' not in st.session_state or st.session_state.dim_size != dim_size or st.session_state.num_bombs != num_bombs:
        st.session_state.board = Board(dim_size, num_bombs)
        st.session_state.game_over = False
        st.session_state.dim_size = dim_size
        st.session_state.num_bombs = num_bombs

    board = st.session_state.board

    if st.session_state.game_over:
        st.text("Game Over!")
        st.table(board.to_dataframe())
        if st.button("Restart"):
            st.session_state.board = Board(dim_size, num_bombs)
            st.session_state.game_over = False
        return

    # Input for user action
    user_input = st.text_input("Enter row,col to dig (e.g., 0,0):")

    if st.button("Submit"):
        if user_input:
            try:
                row, col = map(int, re.split(r',\s*', user_input))
                if row < 0 or row >= board.dim_size or col < 0 or col >= board.dim_size:
                    st.error("Invalid location. Try again.")
                else:
                    safe = board.dig(row, col)
                    if not safe:
                        st.session_state.game_over = True
                        st.error("Game Over! You dug a bomb.")
            except ValueError:
                st.error("Invalid input format. Please enter row,col.")
    
    # Display the current state of the board
    if not st.session_state.game_over:
        st.table(board.to_dataframe())

if __name__ == "__main__":
    main()
