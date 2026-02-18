from ddragon import get_latest_version, get_champion_icon_path
from PIL import Image

version = get_latest_version()
print("Latest patch:", version)

path = get_champion_icon_path("Jax", version=version)
print("Cached icon path:", path)

img = Image.open(path)
print("Icon size:", img.size)
