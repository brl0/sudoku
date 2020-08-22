import torch
from PIL import Image
import numpy as np

torch.load('model.pth')


from pathlib import Path
image_path = Path(r'C:\local\temp\sudoku')


images = image_path.glob('*.png')
imgs = []
for image in images:
    img = Image.open(image)
    img = img \
      .convert('L') \
        .crop((7, 6, 56, 56)) \
          .resize((28, 28))
    img.save(str(image_path / (image.stem + '_28.png')))
    a = np.array(img) / 255
    a = a.reshape((1, 28, 28))
    a = a.astype(np.double)
    imgs.append(a)
with torch.no_grad():
    t = torch.tensor(imgs).float()
    output = network(t)
