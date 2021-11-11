import pandas
import re,os
import requests
class get_info(object):
    '''This class is for catching biosample's attribute.'''
    def __init__(self):
        self.simplify()
        self.main()
        self.input_gate = 'net'
        self.na_ph = self.get_input()
        self.refined()
    
    def get_input(self):
        na_ph = []
        for file in os.listdir(self.input_gate):
            name = os.path.basename(file)[:-4]
            path = os.path.join(self.input_gate,file)
            na_ph.append([name,path])
        return na_ph

    def simplify(self):
        df = pandas.read_csv('prokaryotes.csv')
        new = pandas.DataFrame()
        new['Strain'] = df['Strain']
        new['BioSample'] = df['BioSample']
        new['Level'] = df['Level']
        new['GenBank FTP'] = df['GenBank FTP']
        new.to_csv('Kv.tsv',sep='\t',index=False)

    def main(self):
        head_num = 1
        for line in open('Kv.tsv'):
            if head_num:
                head_num -= 1
                continue
            strain,biosample = line.split('\t')[0:2]
            url = 'https://www.ncbi.nlm.nih.gov/biosample/{}/'.format(biosample)
            r = requests.get(url)
            with open('net/{}.xml'.format(strain),'w') as f:
                f.write(r.text)
        
    def refined(self):
        total = []
        for bsname,path in self.na_ph:
            sample = {}
            with open(path) as f:
                content = f.read()
            record = re.findall('<tr><th>(.*?)</th><td>(.*?)</td></tr>',content)
            for rec in record:
                sample.update({rec[0]:rec[1]})
            total.append([bsname,sample])
        for bs,s in total:
            sdf = pandas.DataFrame([s])
            sdf.to_csv('temp/{}.tsv'.format(bs),sep='\t',index=False)
        i = 1
        for file in os.listdir('temp'):
            if i:
                df1 = pandas.read_csv('temp/{}'.format(file),sep='\t').astype(str)
                i -= 1
                continue
            df2 = pandas.read_csv('temp/{}'.format(file),sep='\t').astype(str)
            df1 = pandas.merge(df1,df2,how='outer')
        df1.to_csv('kv_output.tsv',sep='\t',index=False)

if __name__ == '__main__':
    get_info()

