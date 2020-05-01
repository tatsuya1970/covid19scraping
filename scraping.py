import urllib.request
from bs4 import BeautifulSoup

def Scraping(url:str,table_number:int)->list:
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('Referer', 'http://localhost'),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36 Edg/79.0.309.65'),
    ]

    html = opener.open(url)
    bs = BeautifulSoup(html, 'html.parser')

    table = bs.findAll('table')[table_number]
    trs = table.findAll('tr')

    table_data = []
    for i in range(len(trs)):
        cells = trs[i].findAll(['td', 'th'])
        row = []
        for cell in cells:
            cell_str = cell.get_text()
            #header cleaning
            if i == 0:
                cell_str = cell_str.replace(' ', '').replace(' ','')
            row.append(cell_str)
        table_data.append(row)
    return table_data
