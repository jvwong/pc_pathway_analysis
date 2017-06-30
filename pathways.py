import json
import os
import csv
import requests
import pandas as pd
import re

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
BLACKLIST = ['CTD']
# Grab the section section deliomited by blank line
# 1. PATHWAY_URI	DISPLAY_NAME	DIRECT_SUB_PATHWAY_URIS	ALL_SUB_PATHWAY_URIS
# 2. PATHWAY_URI	DATASOURCE	DISPLAY_NAME	ALL_NAMES	NUM_DIRECT_COMPONENT_OR_STEP_PROCESSES
# So, the first section is about pathways-subpathways hierarchy, while the second
# lists each pathway with its source, names, the number of sub-processess
# Filter out BLACKLIST and those where NUM_DIRECT_COMPONENT_OR_STEP_PROCESSES is 0
for root, dirs, files in os.walk(DATA_DIR, topdown=False):
    for name in files:
        if os.path.splitext(name)[0] in '.txt':
            continue

        fsource = os.path.join(root, name)
        ftarget = os.path.join(RESULTS_DIR, os.path.splitext(name)[0] + '_s2.txt')

        with open(fsource, 'r') as infile, open(ftarget, 'w') as outfile:
            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')
            record = False
            for idx, row in enumerate(reader):
                if not row:
                    record = True
                    continue
                else:
                    if record:
                        if row[1] in BLACKLIST:
                            continue
                        elif row[4] in '0':
                            continue
                        else:
                            writer.writerow(row);


## try a merge on keys
pathways_v8 = pd.read_table(os.path.join(RESULTS_DIR, 'pathways_v8_s2.txt'), header=0, index_col=0)
pathways_v9 = pd.read_table(os.path.join(RESULTS_DIR, 'pathways_v9_s2.txt'), header=0, index_col=0)

merged_v8_v9 = pd.merge(pathways_v8,
    pathways_v9,
    left_index=True,
    right_index=True,
    how = 'inner',
    suffixes=('', '_v9'))

fmerged = os.path.join(RESULTS_DIR, 'merged.txt')
merged = merged_v8_v9[['DATASOURCE', 'DISPLAY_NAME', 'ALL_NAMES', 'NUM_DIRECT_COMPONENT_OR_STEP_PROCESSES']]
merged.to_csv(path_or_buf=fmerged,
    sep='\t',
    na_rep='',
    header=True,
    index=True,
    index_label='PATHWAY_URI')

### Merge with v9 to see what it 'extra'
# merged_outer_v9 = pd.merge(merged,
#     pathways_v9,
#     left_index=True,
#     right_index=True,
#     how = 'outer',
#     suffixes=('', '_v9'),
#     indicator = 'version')
#
# fouterv9 = os.path.join(RESULTS_DIR, 'merged_outer_v9.txt')
# merged_outer_v9.to_csv(path_or_buf=fouterv9,
#     sep='\t',
#     na_rep='',
#     header=True,
#     index=True,
#     index_label='PATHWAY_URI')

## results
# print(pathways_v8.shape)
# print(pathways_v9.shape)
# print(merged.shape)
# v8 (-CTD) - 4855
# v9        - 4448
# merged    - 4118 or 93%
## extra in v9: Panther(5); Reactome(76); SMPDB(7); HumanCyc(242)
