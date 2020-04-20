import csv
import datetime
import pytz
import scraping

TARGET_START_DATE = "2020-04-06T00:00:00+09:00"

class ContactsReader:
    def __init__(self, now, url='https://www.pref.hiroshima.lg.jp/soshiki/50/korona-soudan-kennsai.html'):
        self.data = scraping.Scraping(url)
        self.date = now

    def make_contacts_dict(self):
        contacts = {
            'date':self.date,
            'data':[]
        }

        #inspections data
        # TODO: headerをスクレイピングデータから取りたいが、
        #       ヘッダーが2行に渡るのと、1カラムに2件の情報が入っているのでとりあえず直接定義
        headers = []
        headers.append(self.data[0][0])
        for col in self.data[1]:
            headers.append(col)
        headers.append(self.data[0][-1])

        maindatas = self.data[2:]
        contacts_data = []
        for data in maindatas:
            dic = {}
            for i in range(len(headers)):
                dic[headers[i]] = data[i].replace(',','')
            contacts_data.append(dic)

        contacts['data'] = contacts_data
        return contacts

    def make_contacts_summary_dict(self):
        contacts = self.make_contacts_dict()
        summary = {'data': self.calc_contacts_summary(contacts), 'date': self.date}
        return summary

    def calc_contacts_summary(self, contacts:dict)->list:
        summary = self.import_csv()  # HPから取得できない過去分をCSVで投入
        tz = pytz.timezone('Asia/Tokyo')
        for data in contacts['data']:
            day = {
                '日付':'',
                'date':'',
                'short_date':'',
                '小計':0
            }
            s = "2020-{date}".format(date=data['相談日'].replace('/', '-'))
            try:
                yd = datetime.datetime.strptime(s, '%Y-%m-%d')
                target_date = tz.localize(yd)
            except ValueError:
                continue
            day['日付'] = target_date.isoformat()
            day['date'] = yd.strftime('%Y-%m-%d')
            day['short_date'] = yd.strftime('%m/%d')
            day['小計'] = int(data['合計'])
            summary.append(day)

        return summary

    def import_csv(self):
        summary = []
        with open('./import/contacts.csv') as f:
            rows = [row for row in csv.reader(f)]
            maindatas = rows[1:]
        for v in maindatas:
            data = {
                '日付': v[0],
                'date': v[1],
                'short_date': v[2],
                '小計': int(v[3]),
            }
            summary.append(data)
        return summary
