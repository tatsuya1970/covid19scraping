import datetime
import scraping

class InspectionsReader:
    def __init__(self, now, url='https://www.pref.hiroshima.lg.jp/soshiki/50/korona-kensazisseki.html'):
        self.data = scraping.Scraping(url)
        self.date = now
        print(self.data)
