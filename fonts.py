# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
from pathlib import Path
import subprocess


# %%
from fontTools.ttLib import TTFont


# %%
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


# %%



# %%



# %%



# %%
text_dir = Path('/work/brl0/training/fonts/text')


# %%
for i in range(10):
    text_file = Path(text_dir) / f'{i}.txt'
    text_file.touch()
    text_file.write_text(str(i))


# %%



# %%
fonts = get_ipython().getoutput('convert -list font | grep ttf')
fonts


# %%
fonts = [f.split()[1] for f in fonts]
fonts


# %%
TTF_PATH = fonts[0]
TTF_PATH


# %%
ttf = TTFont(TTF_PATH, 0, allowVID=0, ignoreDecompileErrors=True, fontNumber=-1)


# %%
for f in fonts:
    print(Path(f).stem)


# %%



# %%



# %%
char_codes = list(range(48, 58))
char_codes


# %%
chars = [chr(c) for c in char_codes]
chars


# %%
ttf["cmap"].tables[0].cmap


# %%
FONT_SIZE = '24'


# %%
img_dir = Path('/work/brl0/training/fonts/images')


# %%
for f in fonts:
    ttf_path = Path(f)
    for i in range(10):
        input_txt = str(text_dir / f'{i}.txt')
        output_png = str(img_dir / f'{i}_{ttf_path.stem}.png')
        subprocess.call(["convert", "-font", ttf_path, "-pointsize", FONT_SIZE, "-background", "rgba(0,0,0,0)", "label:@" + input_txt, output_png])


# %%
get_ipython().system('convert')


# %%



# %%



# %%
get_ipython().system('tesseract')


# %%
pytesseract.pytesseract.tesseract_cmd = 'tesseract'


# %%



# %%



# %%



# %%
for img in sorted(img_dir.glob('*.png')):
    num = str(img.stem).split('_')[0]
    image = Image.open(img)
    result = pytesseract.image_to_string(image)
    print(num, result)


# %%
