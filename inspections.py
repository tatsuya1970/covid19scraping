import csv
import datetime
import pytz
import scraping
import mojimoji

class InspectionsReader:
    def __init__(self, now, url='https://www.pref.hiroshima.lg.jp/soshiki/50/korona-kensazisseki.html'):
        self.data = scraping.Scraping(url, 0)
        self.date = now

    def make_inspections_dict(self):
        inspections = {
            'date':self.date,
            'data':[]
        }

        #inspections data
        # TODO: headerをスクレイピングデータから取りたいが、
        #       ヘッダーが3行に渡るのと、1カラムに2件の情報が入っているのでとりあえず直接定義
        headers = [
            '検査実施日',
            '広島市(検査件数)',
            '広島市(陽性件数)',
            '呉市(検査件数)',
            '呉市(陽性件数)',
            '福山市(検査件数)',
            '福山市(陽性件数)',
            '県保健所管内分(検査件数)',
            '県保健所管内分(陽性件数)',
            '合計(検査件数)',
            '合計(陽性件数)'
        ]
        maindatas = self.data[3:]
        inspections_data = []

        # 検査件数と陽性件数を別項目に分割する
        for data in maindatas:
            wk = []
            for i in range(len(data)):
                if i == 0:
                    continue
                s = mojimoji.zen_to_han(data[i])    # 括弧が全半角混じっているので半角に置換
                s = s.replace(',','').split('(')    # 数値の区切り文字,を除去し、前括弧(で分割 e.g: ['100','50)']
                if len(s) == 1:
                    s[0] = s[0].replace('\xa0','0')  # スペースの場合は0に置換
                    s.append('0')   # 陽性件数がない項目は0を付与
                elif len(s) == 2:
                    s[1] = s[1].replace(')', '')    # 検査/陽性件数が正しく分割できた場合は後括弧)を除去

                wk.append(s[0])
                wk.append(s[1])

            dic = {}
            for i in range(len(headers)):
                if i == 0:
                    dic[headers[i]] = data[i]
                    continue

                dic[headers[i]] = wk[i-1]
            inspections_data.append(dic)

        inspections['data'] = inspections_data
        return inspections

    def make_inspections_summary_dict(self):
        inspections = self.make_inspections_dict()
        summary = self.calc_inspections_summary(inspections)
        summary['date'] = self.date
        return summary

    def make_patients_summary_dict(self):
        inspections = self.make_inspections_dict()
        summary = self.calc_patients_summary(inspections)
        return summary

    def calc_inspections_summary(self, inspections:dict)->dict:
        # HPから取得できない過去分をCSVで投入
        summary = self.import_inspections_summary_from_csv()
        tz = pytz.timezone('Asia/Tokyo')
        for data in inspections['data']:
            # 注釈を取って年を付与
            s = "2020/{date}".format(date=data['検査実施日'].replace('※', ''))
            try:
                yd = datetime.datetime.strptime(s, '%Y/%m/%d')
                target_date = tz.localize(yd)
            except ValueError:
                continue

            summary['data']['都内'].append(int(data['合計(検査件数)']))
            summary['data']['その他'].append(0) # とりあえず使って無さそうなので0固定セット
            # summary['labels'].append(data['検査実施日'].replace('/','/'))     # TODO: jsonにescape\を1つだけ挿入する方法が分からない
            summary['labels'].append(yd.strftime('%m/%d'))
        return summary

    def calc_patients_summary(self, inspections:dict)->dict:
        summary = []
        tz = pytz.timezone('Asia/Tokyo')
        for data in inspections['data']:
            day = {
                '日付':'',
                '小計':0
            }
            # 注釈を取って年を付与
            s = "2020/{date}".format(date=data['検査実施日'].replace('※', ''))
            try:
                target_date = tz.localize(datetime.datetime.strptime(s, '%Y/%m/%d'))
            except ValueError:
                continue
            day['日付'] = target_date.isoformat()
            day['小計'] = int(data['合計(陽性件数)'])
            summary.append(day)

        return summary

    def import_inspections_summary_from_csv(self):
        summary = {
            'data': {
                '都内': [],
                'その他': []
            },
            'labels': []
        }
        with open('./import/inspections_summary.csv') as f:
            rows = [row for row in csv.reader(f)]
            maindatas = rows[1:]
        for v in maindatas:
            summary['data']['都内'].append(int(v[0]))
            summary['data']['その他'].append(int(v[1]))
            summary['labels'].append(v[2])
        return summary
