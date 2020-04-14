import re
import datetime
import urllib.request
from bs4 import BeautifulSoup

START_YEAR = 2020
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

class PatientsReader:
    def __init__(self, url='https://www.pref.hiroshima.lg.jp/soshiki/57/bukan-coronavirus.html'):
        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('Referer', 'http://localhost'),
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36 Edg/79.0.309.65'),
        ]

        html = opener.open(url)
        bs = BeautifulSoup(html, 'html.parser')

        table = bs.findAll('table')[0]
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

        self.data = table_data
        #self.date = datetime.datetime.now(JST).isoformat()
        self.date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')


    def make_patients_dict(self):
        patients = {
            'date':self.date,
            'data':[]
        }

        #patients data
        headers = self.data[0]
        maindatas = self.data[1:]
        patients_data = []

        print ('len(headers) = ',len(headers))

        #rewrite header 公表日 as リリース日
        for i in range(len(headers)):

            if headers[i] == '確定日':
                headers[i] = 'リリース日'

            if headers[i] == '詳細情報':
                headers[i] = '退院'



        prev_month = 0 #to judge whether now is 2020 or more
        for data in maindatas:
            dic = {}
            for i in range(len(headers)):

                if headers[i] == '\u3000':
                    continue

                if headers[i] == '主な症状':
                    continue


                dic[headers[i]] = data[i]
                #translate MM/DD to ISO-8601 datetime

                if headers[i] == 'リリース日':
                    md = data[i].split('月')
                    year = START_YEAR
                    month = int(md[0])
                    day = int(md[1].replace('日',''))
                    
                    #2021 or more
                    if month < prev_month:
                        year = START_YEAR + 1

                    date = datetime.datetime(year, month, day, tzinfo=JST)
                    date_str = date.isoformat()
                    prev_month = month
                    #rewrite 公表日 as リリース日
                    dic[headers[i]] = date_str


                if headers[i] == '居住地':
                    if data[i].find('（') > -1:
                        dic[headers[i]]= dic[headers[i]].split('（')[0]

                if headers[i] == '年代':
                    if data[i].find('非公表') > -1:
                        dic[headers[i]] = "非公表"
                    elif data[i].find('詳細情報のとおり') > -1:
                        dic[headers[i]] = "該当の自治体のHP参照"
                    else: dic[headers[i]] = data[i] + "代"

                if headers[i] == '性別':
                    if data[i].find('男') > -1:
                        dic[headers[i]] = "男性"
                    elif data[i].find('女') > -1:
                        dic[headers[i]] = "女性"
                    elif data[i].find('詳細情報のとおり') > -1:
                        dic[headers[i]] = "該当の自治体のHP参照"

                if headers[i] == '退院':
                    if data[i].find('退院') > -1:
                        dic[headers[i]] = "〇"
                    else: dic[headers[i]] = ""

                if dic[headers[i]].find('\n') > -1:
                    dic[headers[i]] = dic[headers[i]].replace('\n','')




            patients_data.append(dic)

        patients['data'] = patients_data
        return patients

    def make_patients_summary_dict(self):
        patients = self.make_patients_dict()
        summary = self.calc_patients_summary(patients)
        patients_summary = {'data': summary, 'date': self.date}
        return patients_summary

    #sample:最終更新日：2020年3月05日（木）
    def parse_datetext(self, datetext:str)->str:
        parsed_date = re.split('[^0-9]+', datetext)[1:4]
        year = int(parsed_date[0])
        month = int(parsed_date[1])
        day = int(parsed_date[2])
        date = datetime.datetime(year, month, day, tzinfo=JST)
        date_str = date.isoformat()
        return date_str

    def calc_patients_summary(self, patients:dict)->list:
        summary = []

        start_day = patients['data'][0]['リリース日']
        start_datetime = datetime.datetime.fromisoformat(start_day)

        end_datetime = datetime.datetime.fromisoformat(patients['date'])
        while start_datetime <= end_datetime:
            day = {
                '日付':'',
                '小計':0
            }
            day['日付'] = start_datetime.isoformat()
            
            for p in patients['data']:
                if p['リリース日'] == day['日付']:
                    day['小計'] = day['小計'] + 1

            summary.append(day)
            start_datetime = start_datetime + datetime.timedelta(days=1)

        return summary


f1 = PatientsReader()
print(f1.make_patients_dict())
