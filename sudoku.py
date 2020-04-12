import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import time

from loguru import logger
import numpy as np
import pyautogui, pytesseract, cv2
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\b_r_l\scoop\apps\tesseract\current\tesseract.exe"

pyautogui.PAUSE = 0.07

SCREENSHOT_DIR = '/Users/b_r_l/OneDrive/Pictures/Screenshots/sudoku/'

X_START = 780
X_END = 1500
X_SIZE = (X_END - X_START) // 9
Y_START = 160
Y_END = 880
Y_SIZE = (Y_END - Y_START) // 9
borderx = 5
bordery = 5


def rec_img(path):
    config = '--oem 1 --psm 10 -c tessedit_char_whitelist=123456789'
    img = str(path)
    name = path.stem.replace('-cv2', '')
    x, y = name.split('_')
    text = pytesseract.image_to_string(img, config=config)
    if text:
        val = int(text[0])
    else:
        val = 0
    return int(x), int(y), val


class Game:
    def get_grid_img(self):
        for i in range(9):
            for j in range(9):
                img_path = SCREENSHOT_DIR + str(i) + '_' + str(j) + '.png'
                pyautogui.screenshot(img_path,
                                     region=(X_START + j * X_SIZE + borderx,
                                             Y_START + i * Y_SIZE + bordery,
                                             X_SIZE - borderx * 2,
                                             Y_SIZE - bordery * 2))
        logger.info("Finished getting grid images.")

    async def img_to_text(self):
        empty_board = np.zeros((9, 9))
        grid = np.zeros((9, 9))
        futures_grid = [[list() for j in range(9)] for i in range(9)]
        with ProcessPoolExecutor as executor:
            for i in range(9):
                for j in range(9):
                    img_base = SCREENSHOT_DIR + str(i) + '_' + str(j)
                    img_path = img_base + '.png'
                    img = Image.open(img_path).convert('L')
                    ret, img = cv2.threshold(np.array(img), 125, 255, cv2.THRESH_BINARY)

                    img = Image.fromarray(img.astype(np.uint8))
                    w, h = img.size
                    xd, yd = 5, 5
                    img = img.crop((xd, yd, w - xd, h - yd))
                    img.save(img_base + '-cv2.png')

                    future_text = executor.submit(rec_img, img)
                    futures_grid[i][j] = future_text
            for i in range(9):
                for j in range(9):
                    text = await futures_grid[i][j].result()
                    if not text:
                        empty_board[i][j] = 1
                        text = 0
                    grid[i][j] = int(str(text)[0])
        self.empty_board = empty_board
        self.board = grid

    async def get_grid(self):
        self.get_grid_img()
        await self.img_to_text()
        logger.info("Done recognizing board.")
        print('Original board:\n', self.board, '\n')

    def possible(self, y, x, n):
        for i in range(9):
            if self.board[y][i] == n:
                return False

        for i in range(9):
            if self.board[i][x] == n:
                return False

        gridx = (x // 3) * 3
        gridy = (y // 3) * 3

        for i in range(3):
            for j in range(3):
                if self.board[gridy + i][gridx + j] == n:
                    return False

        return True

    def solving(self):
        for y in range(9):
            for x in range(9):
                if self.board[y][x] == 0:
                    for n in range(1, 10):
                        if self.possible(y, x, n):
                            self.board[y][x] = n
                            solved = self.solving()
                            if solved:
                                return True
                            self.board[y][x] = 0
                    return False
        return True

    def solve(self):
        self.solving()
        return self.board

    def write(self):
        for y in range(9):
            for x in range(9):
                if self.empty_board[y][x] == 1:
                    pyautogui.click(X_START + X_SIZE // 2 + X_SIZE * x,
                                    Y_START + Y_SIZE // 2 + Y_SIZE * y)
                    pyautogui.write(str(self.board[y][x]))


if __name__ == '__main__':
    logger.info(f'Started: {time.process_time()}')
    game = Game()
    # asyncio.run(game.get_grid())
    # logger.info('Solving.')
    # game.solve()
    # logger.info(f'Done. {time.process_time()}')
    # print('Solved board:\n', game.board)
    # game.write()
