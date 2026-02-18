import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

img = Image.open(".cache/ddragon/16.4.1/img/champion/Jax.png").convert("RGBA")

plt.figure(figsize=(6, 2))
ax = plt.gca()
ax.set_xlim(0, 10)
ax.set_ylim(0, 1)

oi = OffsetImage(np.asarray(img), zoom=0.4)
ab = AnnotationBbox(oi, (5, 0.5), frameon=False)
ab.set_clip_on(False)
ab.set_zorder(10)
ax.add_artist(ab)

plt.show()
