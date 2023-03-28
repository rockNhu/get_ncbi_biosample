# get_ncbi_biosample
This python script is to get infomation from BioSample database in NCBI with BioSample IDs.

## 1 get BioSample IDs
First, search with a term in [NCBI/BioSample](https://www.ncbi.nlm.nih.gov/biosample).
Then, `Send to` -> `file` -> `Format=BioSample ID List`.
Finally, wait the id list download.

## 2 get info with python
```bash
python get_ncbi_biosample2.py -i BioSample_id.txt -o final.tsv
```

## 3 filt
Using Excel filt the infomation which is not relative or not important.
