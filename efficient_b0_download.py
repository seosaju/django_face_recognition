import ssl
from urllib.request import urlopen

ssl._create_default_https_context = ssl._create_unverified_context
result = urlopen("https://github.com/lukemelas/EfficientNet-PyTorch/releases/download/1.0/efficientnet-b0-355c32eb.pth")
