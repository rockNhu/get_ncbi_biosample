import pandas
import re
import os
import pathlib
import requests
import argparse


class get_info(object):
    '''This class is for catching biosample's attribute.'''

    def __init__(self):
        self.args = self.args_parser()
        self.simplify()
        self.main()
        self.refined()

    def args_parser(self):
        parser = argparse.ArgumentParser(
            description='This script is used to get biosamples in NCBI.')
        parser.add_argument('-i', '--input', required=True,
            help='Path of input tsv,\
            the ncbi_table must include "Assembly Accession" and\
            "Assembly BioSample Accession" columns.'
            )
        parser.add_argument('-o', '--output', required=True,
            help='Path to output.'
            )
        return parser.parse_args()

    def get_input(self, gate):
        '''List the xml dir.'''
        na_ph = []
        for file in os.listdir(gate):
            name = os.path.basename(file).rsplit('.', 1)[0]
            path = os.path.join(gate, file)
            na_ph.append([name, path])
        return na_ph

    def simplify(self):
        '''The table is download from NCBI, and just need 2 columns now.'''
        df = pandas.read_csv(self.args.input, sep='\t')
        new = pandas.DataFrame()
        new['Strain'] = df['Assembly Accession']
        new['BioSample'] = df['Assembly BioSample Accession']
        new.to_csv('temp.tsv', sep='\t', index=False)

    def main(self):
        '''Get the biosample and save to xml.'''
        if not os.path.exists('net'):
            os.mkdir('net')
        head_num = 1
        for line in open('temp.tsv'):
            if head_num:
                head_num -= 1
                continue
            strain, biosample = line.strip().split('\t')
            if os.path.exists(f'net/{strain}.xml'):
                continue
            url = f'https://www.ncbi.nlm.nih.gov/biosample/{biosample}/'
            r = requests.get(url)
            with open(f'net/{strain}.xml', 'w') as f:
                f.write(r.text)

    def refined(self):
        '''The final filter, get the annotation table.'''
        if not os.path.exists('temp'):
            os.mkdir('temp')
        total = []
        for bsname, path in self.get_input('net'):
            content = pathlib.Path(path).read_text()
            record = re.findall(
                '<tr><th>(.*?)</th><td>(.*?)</td></tr>', content)
            sample = {rec[0]: rec[1] for rec in record}
            total.append([bsname, sample])
        for bs, s in total:
            sdf = pandas.DataFrame([s])
            sdf.to_csv(f'temp/{bs}.tsv', sep='\t', index=False)
        i = 1
        for file in os.listdir('temp'):
            if i:  # the first line
                df1 = pandas.read_csv(f'temp/{file}', sep='\t').astype(str)
                i -= 1
                continue
            df2 = pandas.read_csv(f'temp/{file}', sep='\t').astype(str)
            df1 = pandas.merge(df1, df2, how='outer')
        df1.to_csv(self.args.output, sep='\t', index=False)


if __name__ == '__main__':
    get_info()
