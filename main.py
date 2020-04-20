import csv
import json
import datetime
import glob
import os
from patients import PatientsReader
from inspections import InspectionsReader
from contacts import ContactsReader

JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

class CovidDataManager:
    def __init__(self):
        self.data = {
            'patients':{},
            'discharges_summary':{},
            'patients_summary':{},
            'inspections_summary':{},
            'contacts':{},
            'inspections':{},
            'last_update':datetime.datetime.now().strftime('%Y/%m/%d %H:%M'),
            # 'querents':{},
            # 'discharges':{},
            # 'better_patients_summary':{},
            # 'main_summary':{}
        }

    def fetch_data(self):
        pr = PatientsReader(self.data['last_update'])
        ir = InspectionsReader(self.data['last_update'])
        cr = ContactsReader(self.data['last_update'])

        self.data['patients'] = pr.make_patients_dict()
        self.data['inspections'] = ir.make_inspections_dict()
        self.data['inspections_summary'] = ir.make_inspections_summary_dict()
        self.data['discharges_summary'] = pr.make_discharges_summary_dict()

        # 陽性患者数は範囲日付でまとめられて正確に取得できないので、
        # 4/5以前以後を別のデータから取得してきて1つにマージする
        wk_patients_summary = pr.make_patients_summary_dict()
        wk_patients_summary.extend(ir.make_patients_summary_dict())
        self.data['patients_summary'] = {'data': wk_patients_summary, 'date': self.data['last_update']}

        self.data['contacts'] = cr.make_contacts_summary_dict()


    def export_csv(self):
        for key in self.data:
            if key == 'last_update' or key == 'main_summary' or key == 'inspections_summary':
                continue

            datas = self.data[key]
            if datas == {}:
                continue

            maindatas = datas['data']
            header = list(maindatas[0].keys())
            csv_rows = [ header ]
            for d in maindatas:
                csv_rows.append( list(d.values()) )

            with open('data/' + key + '.csv', 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(csv_rows)

    def export_json(self, filepath='data/data.json'):
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def import_csv(self):
        csvfiles = glob.glob('./import/*.csv')
        for csvfile in csvfiles:
            filename = os.path.splitext(os.path.basename(csvfile))[0]
            last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(csvfile), JST).isoformat()
            datas = []
            with open(csvfile) as f:
                rows = [row for row in csv.reader(f)]
                header = rows[0]
                maindatas = rows[1:]
                for d in maindatas:
                    data = {}
                    for i in range(len(header)):
                        data[header[i]] = d[i]
                        if header[i] == '小計':
                            data[header[i]] = int(d[i])
                    datas.append(data)

            self.data[filename] = {
                'data':datas,
                'date':last_modified_time
            }

if __name__ == "__main__":
    dm = CovidDataManager()
    dm.fetch_data()
    # dm.import_csv()   広島に関してはcsvインポートが不要だと思うのでコメントアウト
    dm.export_csv()
    dm.export_json()
