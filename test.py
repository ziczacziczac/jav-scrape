import urllib.request

for i in range(10):
    print(i)
    try:
        res = urllib.request.urlopen('https://fvs.io/redirector?token=dkVHa0dQMmhaUmFteTZYTEZyM2lJc3JZMVFCSEg5bFNOSlhTUEZsQUs5V2J0c3RScmpkVnVHTUVQbUZwWGo5SFBEamxvaGtJcU1LL2lUTTh1eDhPZGNzZ2grY3NRKytmcUhidEViaWN2Z3h1d08xcU9JY2pLbHU4ZWJHN00rRitoK3BqMm90YnA4NHV2RkhhaUtKZmJWcjlEYzJHbzFvdTFzeHQ6WlNRaGhMQWdaQTVQalMyeEtpdGdkUT09')
        finalurl = res.geturl()
        print(res.getcode())
        print(finalurl)
    except Exception as e:
        print(str(e))
