"""Content completeness checks; visual QA is a separate mandatory review."""
from pathlib import Path
import json
import re
from zipfile import ZipFile
from lxml import etree
from build_materials import COVERAGE, ROOT, manual_filename

def main():
    errors=[]; rows=[]
    for n in range(1,17):
        folder=ROOT/'labs'/f'{n:02d}'
        text=(folder/'README.md').read_text(encoding='utf-8')
        for section in ['Цель','Развёрнутый порядок выполнения','Полный демонстрационный вариант','Что сдать','Критерии приёмки','Типичные ошибки','Самопроверка перед сдачей']:
            if section not in text: errors.append(f'{n}: missing {section}')
        if len(re.findall(r'### Шаг \d',text))!=6: errors.append(f'{n}: step count')
        if '{{' in text: errors.append(f'{n}: unresolved marker')
        for label,path in COVERAGE[n]:
            if not path.startswith('https://') and not (folder/'demo'/path).resolve().exists(): errors.append(f'{n}: missing {label}: {path}')
        for image in re.findall(r'!\[.*?\]\((.*?)\)',text):
            if not (folder/image).resolve().exists(): errors.append(f'{n}: missing image {image}')
        docx=folder/manual_filename(n)
        with ZipFile(docx) as z:
            x=etree.fromstring(z.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            body=' '.join(x.xpath('//w:t/text()',namespaces=ns))
            if len(body)<6000: errors.append(f'{n}: unexpectedly short document')
            for part in ['word/document.xml','word/styles.xml']:
                if b'pBdr' in z.read(part): errors.append(f'{n}: paragraph border residue')
        rows.append({'lab':n,'requirements':len(COVERAGE[n]),'word_count':len(text.split()),'docx_bytes':docx.stat().st_size})
    metrics=json.loads((ROOT/'demo/results/summary.json').read_text(encoding='utf-8'))
    assert metrics['raw']==42 and metrics['clean']==36
    assert metrics['validation']['baseline']['ndcg']==0.5
    assert metrics['validation']['improved']['ndcg']==1.0
    report={'labs':rows,'errors':errors,'visual_review':'separate PNG review required'}
    out=ROOT/'_qa'; out.mkdir(exist_ok=True)
    (out/'content_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__': main()
