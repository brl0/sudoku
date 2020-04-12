import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import time

from loguru import logger
import numpy as np
import pytesseract, cv2
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\b_r_l\scoop\apps\tesseract\current\tesseract.exe"

SCREENSHOT_DIR = '/Users/b_r_l/OneDrive/Pictures/Screenshots/sudoku/'


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


async def process_images():
    grid = np.zeros((9, 9))
    images = sorted(Path(SCREENSHOT_DIR).glob('*-cv2.png'))
    with ProcessPoolExecutor() as executor:
        results = executor.map(rec_img, images)
    for x, y, val in results:
        grid[x][y] = val
    return grid


if __name__ == '__main__':
    start_time = time.time()
    logger.info(f'Started.')
    grid = asyncio.run(process_images())
    logger.info(f'Done. {time.time() - start_time}')
    print(grid)
