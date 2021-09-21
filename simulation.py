import requests
import time
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt

# Requires added GUI support if used on WSL

url = 'http://127.0.0.1:5000/map'

plt.show(block=False)

while True:
    r = requests.get(url)
    img = np.array(Image.open(BytesIO(r.content)))
    imgplot = plt.imshow(img)
    plt.pause(1)
