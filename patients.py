import re
import datetime
import pytz
import scraping
import mojimoji

START_YEAR = 2020
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
# 感染患者リストから正しく集計可能なend_dateを決定する（以降は検査実施状況ページに任せる）
TARGET_END_DATE = "2020-04-05T00:00:00+09:00"

class PatientsReader:
    def __init__(self, now, url='https://www.pref.hiroshima.lg.jp/soshiki/57/bukan-coronavirus.html'):
        self.data = scraping.Scraping(url)
        self.date = now


    def make_patients_dict(self):
        patients = {
            'date':self.date,
            'data':[]
        }

        #patients data
        headers = self.data[0]
        maindatas = self.data[1:]
        patients_data = []

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
                    if '～' in data[i]:
                        # e.g) 4月13日〜14日
                        dic[headers[i]] = data[i].replace('月', '/').replace('日', '')
                    else:
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
        return summary
    
    def make_discharges_summary_dict(self):
        patients = self.make_patients_dict()
        summary = self.calc_discharges_summary(patients)
        return summary

    def calc_patients_summary(self, patients:dict)->list:
        summary = []

        start_day = patients['data'][0]['リリース日']
        start_datetime = datetime.datetime.fromisoformat(start_day)

        # end_datetime = datetime.datetime.fromisoformat(patients['date'])
        end_datetime = datetime.datetime.fromisoformat(TARGET_END_DATE)
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

    def calc_discharges_summary(self, patients:dict)->list:
        discharges_summary = {
            'date':self.date,
            'data':[]
        }
        summary = []
        maindatas = self.data[1:]

        tz = pytz.timezone('Asia/Tokyo')
        start_day = patients['data'][0]['リリース日']
        start_datetime = datetime.datetime.fromisoformat(start_day)
        end_datetime = datetime.datetime.fromisoformat(patients['date'])
        while start_datetime <= end_datetime:
            day = {
                '日付':start_datetime.isoformat(),
                '小計':0
            }
            for data in maindatas:
                ss = data[-1].split('\n')
                for s in ss:
                    if s.find('退院') >= 0:
                        d = s.replace('退院', '').replace('月','-').replace('日', '')   # 4月15日退院 を4/15に変換
                        yd = "2020-{date}".format(date=mojimoji.zen_to_han(d))
                        try:
                            # TODO: RFC3339の美しい扱い方が分からない
                            target_date = '{date}+09:00'.format(date=datetime.datetime.strptime(yd, '%Y-%m-%d').isoformat('T'))
                        except ValueError:
                            print('[skip] Failed to parse date.{date}'.format(date=s))
                            continue

                        print(day['日付'])
                        print(target_date)

                        if day['日付'] == target_date:
                            day['小計'] += 1
            summary.append(day)
            start_datetime = start_datetime + datetime.timedelta(days=1)

        discharges_summary['data'] = summary
        return discharges_summary


# f1 = PatientsReader()
# print(f1.make_patients_dict())
