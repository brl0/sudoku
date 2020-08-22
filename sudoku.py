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

SCREENSHOT_DIR = '/local/temp/sudoku/'

X_START = 780
X_END = 1500
X_SIZE = (X_END - X_START) // 9
Y_START = 160
Y_END = 880
Y_SIZE = (Y_END - Y_START) // 9
borderx = 5
bordery = 5


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

    @staticmethod
    def proc_img(img_file):
        img_path = str(img_file)
        img = Image.open(img_path).convert('L')
        ret, img = cv2.threshold(np.array(img), 125, 255,
                                    cv2.THRESH_BINARY)
        img = Image.fromarray(img.astype(np.uint8))
        w, h = img.size
        xd, yd = 5, 5
        img = img.crop((xd, yd, w - xd, h - yd))
        clean_img_path = img_path.replace('.png', '-cv2.png')
        img.save(clean_img_path)

    def proc_imgs(self):
        for img_file in sorted(Path(SCREENSHOT_DIR).glob('*.png')):
            self.proc_img(img_file)
        logger.info("Finished cleaning images.")

    @staticmethod
    def rec_img(path):
        config = '--oem 1 --psm 10 -c tessedit_char_whitelist=123456789'
        i, j = path.stem.replace('-cv2', '').split('_')
        i, j = int(i), int(j)
        img_path = str(path)
        text = pytesseract.image_to_string(img_path, config=config)
        if text:
            val = int(text[0])
        else:
            val = 0
        return i, j, val

    def make_board(self):
        empty_board = np.zeros((9, 9))
        grid = np.zeros((9, 9))
        images = sorted(Path(SCREENSHOT_DIR).glob('*-cv2.png'))
        with ProcessPoolExecutor() as executor:
            results = executor.map(self.rec_img, images)
        for i, j, val in results:
            grid[i][j] = val
            if val == 0:
                empty_board[i][j] = 1
        self.empty_board = empty_board
        self.board = grid
        logger.info("Finished making board.")

    def get_grid(self):
        self.get_grid_img()
        self.proc_imgs()
        self.make_board()
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
    start_time = time.time()
    logger.info(f'Started.')
    for f in Path(SCREENSHOT_DIR).glob('*.png'):
        f.unlink()
    game = Game()
    game.get_grid()
    # logger.info('Solving.')
    # game.solve()
    # print('Solved board:\n', game.board)
    # game.write()
    # for f in Path(SCREENSHOT_DIR).glob('*.png'):
    #     f.unlink()
    logger.info(f'Done. {time.time() - start_time}')
