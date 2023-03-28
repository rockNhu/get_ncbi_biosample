# -* coding = UTF-8 *-
# @Author = Shixuan Huang
from Bio import Entrez
import os
import pandas
import pathlib
import re
import ssl
import argparse


class get_ncbi_biosample_info(object):
    '''This class is for catching the biosample infomation with biosample uid list file.'''

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='This script is used to catch the biosample infomation with biosample uid list file')
        parser.add_argument('-i', '--input', required=True,
                            help='Path of input biosample_ids_list.txt, it can be download from NCBI Biosample search file idlist')
        parser.add_argument('-o', '--output', default='final.tsv',
                            required=False, help='Path to output, default is final.tsv')
        self.args = parser.parse_args()
        self.retry = 5
        self.net_dir = 'net'
        self.temp_dir = 'temp'
        self.env_setting()
        self.main()

    def env_setting(self):
        '''setting the running env'''
        def mkdir(d):
            if not os.path.exists(d):
                os.makedirs(d)

        ssl._create_default_https_context = ssl._create_unverified_context
        Entrez.email = 'nhuhuganaxis@outlook.com'
        mkdir(self.net_dir)
        mkdir(self.temp_dir)

    def get_input(self, file):
        '''get input file content, the uids'''
        return [line.strip() for line in open(file)]

    def run_catch(self, uid):
        '''catch the biosample database output with uid'''
        def spider():
            try:
                handle = Entrez.efetch('biosample', id=uid)
                return str(handle.read())
            except Exception:
                return False

        for i in range(self.retry):
            if out := spider():
                print(f'{uid}: ok')
                return out
            else:
                print(f"Error:{uid}, retry times = {i}")
        return False

    def out2net(self, o, o_name):
        '''Output sample net to xml file'''
        with open(f'{self.net_dir}/{o_name}.xml', 'w') as f:
            f.write(o)

    def get_re(self, uid):
        '''Using regular find all phenotype of input xml dir'''
        content = pathlib.Path(f'{self.net_dir}/{uid}.xml').read_text()
        record = re.findall('attribute_name="(.*?)".*?>(.*?)<', content)
        return {rec[0]: rec[1] for rec in record}

    def trans2tsv(self, s, uid):
        '''Translate the regualar found 2 tsv temp.'''
        sdf = pandas.DataFrame([s])
        sdf.to_csv(f'{self.temp_dir}/{uid}.tsv', sep='\t', index=False)

    def combined2out(self, o_name):
        '''The final filter, get the annotation table.'''
        def get_content(file):
            s = {}
            d = {}
            head_num = 1
            for line in open(file):
                content = line.strip().split('\t')
                if head_num:  # head is name of catagory
                    head_num -= 1
                    for idx, i in enumerate(content):
                        s[idx] = i
                    continue
                for idx, i in enumerate(content):
                    d[s[idx]] = i
                break  # the file lines only 2
            return d

        out_dict = {}
        for file in os.listdir(self.temp_dir):
            uid = file.rsplit('.', 1)[0]
            print(f'Current: {uid}')
            d = get_content(os.path.join(self.temp_dir, file))
            out_dict[uid] = d
        o = pandas.DataFrame(out_dict)
        o = o.T
        o.index.name = 'SampleID'
        o.to_csv(o_name,'\t','NA',chunksize=1000)

    def main(self):
        uid_list = self.get_input(self.args.input)
        for uid in uid_list:
            # skip the exists
            if not os.path.exists(f'{self.net_dir}/{uid}.xml'):
                if output := self.run_catch(uid):
                    self.out2net(output, uid)
                else:
                    print(f'{uid} is not ok!')
            if not os.path.exists(f'{self.temp_dir}/{uid}.tsv'):
                r = self.get_re(uid)
                self.trans2tsv(r, uid)
        self.combined2out(self.args.output)


if __name__ == '__main__':
    get_ncbi_biosample_info()
