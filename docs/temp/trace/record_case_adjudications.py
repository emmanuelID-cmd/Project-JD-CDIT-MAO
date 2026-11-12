import hashlib,json
from pathlib import Path
root=Path.cwd(); t=root/'docs/temp/trace'
rp=t/'EVAL-DRAFT-V1-LIVE-TRIAGE.corrected.results.json'
r=json.loads(rp.read_text(encoding='utf-8'))
adjudications=[]
for cid in ('SYN-EVAL-068','SYN-EVAL-070'):
 c=next(x for x in r['cases'] if x['case_id']==cid)
 i=next(x for x in c['items'] if x.get('expected_category') is not None)
 adjudications.append({'case_id':cid,'item_index':i['item_index'],'expected_category':i['expected_category'],'actual_category':i['actual_category'],'decision':'confirmed_failure','adjudicator':'Manny','decision_date':'2026-11-09','basis':'User confirmed the model output is a failure against the expected category.'})
r['case_level_adjudications']=adjudications
for diff in r['triage_category'].get('category_disagreements',[]):
 diff['decision']='confirmed_failure' if diff.get('case_id') in {'SYN-EVAL-068','SYN-EVAL-070'} else diff.get('decision','unadjudicated')
rp.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
addp=t/'EVAL-DRAFT-V1-LIVE-TRIAGE.manifest.addendum.json'
add=json.loads(addp.read_text(encoding='utf-8'))
report=next(t.glob('Trace * Manny-Triage Live100-001 coordinator.md'))
add['corrected_results_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
add['final_trace_report_sha256']=hashlib.sha256(report.read_bytes()).hexdigest()
add['case_level_adjudications']={'cases':['SYN-EVAL-068','SYN-EVAL-070'],'adjudicator':'Manny','decision':'confirmed_failure','scope':'these two cases only; remaining label approvals unchanged'}
addp.write_text(json.dumps(add,indent=2)+'\n',encoding='utf-8',newline='\n')
hp=t/'trace-history.json'; h=json.loads(hp.read_text(encoding='utf-8'))
fp=hashlib.sha256((t/'EVAL-DRAFT-V1-LIVE-TRIAGE.manifest.json').read_bytes()+addp.read_bytes()).hexdigest()
for row in h.get('runs',[]):
 if row.get('trace_id')=='TRACE-ead5e547-773a-44a1-bafa-e34e2fdc9297':
  row['version']=fp; row['failed_checks']=1; row['unverified_checks']=1
hp.write_text(json.dumps(h,indent=2)+'\n',encoding='utf-8',newline='\n')
old=t/'EVAL-DRAFT-V1-LIVE-TRIAGE.md'
if old.exists():
 text=old.read_text(encoding='utf-8')
 note='> **Superseded summary:** The original denominator counted unpaired rows. Use `EVAL-DRAFT-V1-LIVE-TRIAGE.corrected.results.json` and the `Trace ... Manny-Triage Live100-001 coordinator.md` report for reconciled metrics and Manny’s case-level adjudications.\n\n'
 if not text.startswith('> **Superseded summary:**'): old.write_text(note+text,encoding='utf-8',newline='\n')
print('Recorded two owner-confirmed failures; global draft approval flags remain unchanged.')
print('result sha',hashlib.sha256(rp.read_bytes()).hexdigest())
print('trace history updated',fp)