"""Validate the Fabric-only project; --write updates notebook bindings and defaults."""
from pathlib import Path
import argparse
import ast
import csv
import json
import re
import uuid

HERE=Path(__file__).resolve().parent
KEYS=['01_bronze_validation','02_silver','03_gold','04_acceptance']
GUID=r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

def identifier(value,kind):
    if re.fullmatch(GUID,value):return str(uuid.UUID(value))
    pattern=r'/groups/('+GUID+r')' if kind=='workspace' else r'/lakehouses/('+GUID+r')'
    match=re.search(pattern,value)
    if not match:raise ValueError('Invalid '+kind+' URL/UUID')
    return str(uuid.UUID(match.group(1)))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Update local notebook metadata and parameter defaults; never changes Fabric')
    args=parser.parse_args()
    c=json.loads((HERE/'config.json').read_text(encoding='utf-8-sig'))
    workspace=identifier(c['workspace_url'],'workspace');lakehouse=identifier(c['lakehouse_url'],'lakehouse')
    match=re.search(r'/groups/('+GUID+r')',c['lakehouse_url'])
    if match and str(uuid.UUID(match.group(1)))!=workspace:raise ValueError('Workspace and Lakehouse URL disagree')
    for key in ['source_folder','bronze_folder','reports_folder']:
        value=c[key]
        if not isinstance(value,str) or not value or value.startswith(('/','Files/')) or '\\' in value or ':' in value or any(p in ('','.','..') for p in value.split('/')):
            raise ValueError('Invalid relative folder: '+key)
    folders=[c[key] for key in ['source_folder','bronze_folder','reports_folder']]
    if any(a==b or a.startswith(b+'/') or b.startswith(a+'/') for i,a in enumerate(folders) for b in folders[i+1:]):
        raise ValueError('Source, Bronze and Reports folders must not overlap')
    if c['table_schema'] and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',c['table_schema']):raise ValueError('Invalid schema')
    if not isinstance(c['strict_project_snapshot'],bool):raise ValueError('strict_project_snapshot must be a boolean')
    expected={'run_id':'manual',**{k:c[k] for k in ['source_folder','bronze_folder','reports_folder','table_schema','strict_project_snapshot']}}
    binding={'default_lakehouse':lakehouse,'default_lakehouse_name':c['lakehouse_name'],
        'default_lakehouse_workspace_id':workspace,'known_lakehouses':[{'id':lakehouse}]}
    for key in KEYS:
        path=HERE/'prepared'/(key+'.ipynb');nb=json.loads(path.read_text(encoding='utf-8'))
        cells=[cell for cell in nb['cells'] if 'parameters' in cell.get('metadata',{}).get('tags',[])]
        if len(cells)!=1:raise ValueError(key+': expected exactly one parameter cell')
        if args.write:
            cells[0]['source']='\n'.join(f'{k} = {v!r}' for k,v in expected.items()).splitlines(keepends=True)
            nb['metadata'].setdefault('dependencies',{})['lakehouse']=binding
            path.write_text(json.dumps(nb,ensure_ascii=False,indent=2),encoding='utf-8')
        if nb['metadata']['dependencies']['lakehouse']!=binding:raise ValueError(key+': metadata differs from config; use --write')
        # Parse constant assignments only; never execute notebook cells during validation.
        tree=ast.parse(''.join(cells[0]['source']))
        actual={node.targets[0].id:ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign)}
        if actual!=expected:raise ValueError(key+': defaults differ from config; use --write')
        for cell in nb['cells']:
            if cell['cell_type']=='code':ast.parse(''.join(cell['source']))
        print('OK',key+'.ipynb')
    for name,rows,columns in [('mindx_raw_sales_data.csv',5250,15),('exchange_rate_2425.csv',24,5)]:
        with (HERE/'prepared/inputs'/name).open(encoding='utf-8-sig',newline='') as f:
            reader=csv.reader(f);header=next(reader);data=list(reader)
        if len(header)!=columns or any(len(r)!=columns for r in data):raise ValueError('Invalid CSV structure: '+name)
        if c['strict_project_snapshot'] and len(data)!=rows:raise ValueError('Unexpected row count: '+name)
        print('OK',name,len(data),'rows')
    print('Fabric-only project validated. No cloud resources were changed.')

if __name__=='__main__':main()
