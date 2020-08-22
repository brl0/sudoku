import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import time

from loguru import logger
import numpy as np
import pytesseract, cv2
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\b_r_l\scoop\apps\tesseract\current\tesseract.exe"

SCREENSHOT_DIR = '/local/temp/sudoku/missed'


def rec_img(path):
    config = '--oem 1 --psm 10 -c tessedit_char_whitelist=123456789'
    img = str(path)
    text = pytesseract.image_to_string(img, config=config)
    return path.stem, text


async def process_images():
    images = sorted(Path(SCREENSHOT_DIR).glob('*.png'))
    with ProcessPoolExecutor() as executor:
        results = executor.map(rec_img, images)
    return [*results]


if __name__ == '__main__':
    start_time = time.time()
    logger.info(f'Started.')
    results = asyncio.run(process_images())
    logger.info(f'Done. {time.time() - start_time}')
    for name, val in results:
        print(name, val)
