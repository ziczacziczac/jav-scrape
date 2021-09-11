import urllib.request
import wget

url = 'https://www928.ff-02.com/token=0REpP2jI7-bIpOzzpzc-GA/1631208424/27.72.0.0/178/4/1d/be12e41291de5ceb45746e6b7e0531d4-480p.mp4'
filename = wget.download(url)
print(filename)
