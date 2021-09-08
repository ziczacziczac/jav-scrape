import urllib.request
import wget

url = 'https://www2175.ff-05.com/token=vJ4IytPF5xDh87DXsafoBw/1630990513/2405:4802::/178/4/1d/be12e41291de5ceb45746e6b7e0531d4-480p.mp4'
filename = wget.download(url)
print(filename)
