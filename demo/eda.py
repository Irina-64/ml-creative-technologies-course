"""Six reproducible SVG charts from actual demo data, without third-party modules."""
from collections import Counter
import csv
from html import escape
from .project import DATA, RESULTS, read_json, save_csv, save_json

def make_chart(name,title,labels,values,interpretation):
    width=950; height=120+60*len(labels)
    max_value=max(values) or 1
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="25" y="36" font-family="Arial" font-size="22">{escape(title)}</text>']
    for i,(label,value) in enumerate(zip(labels,values)):
        y=65+i*60
        svg.extend([f'<text x="25" y="{y+24}" font-family="Arial" font-size="18">{escape(str(label))}</text>',
                    f'<rect x="330" y="{y}" width="{500*value/max_value}" height="32" fill="#2563A6"/>',
                    f'<text x="{340+500*value/max_value}" y="{y+24}" font-family="Arial" font-size="18">{value}</text>'])
    svg.append('</svg>')
    path=RESULTS/'figures'/f'{name}.svg'; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(svg),encoding='utf-8')
    return dict(name=name,title=title,labels=labels,values=values,interpretation=interpretation)

def run():
    raw=read_json(DATA/'raw.json'); clean=read_json(DATA/'clean.json')
    charts=[]
    def chart(name,title,counter,note): charts.append(make_chart(name,title,list(counter),list(counter.values()),note))
    chart('01_genres','Жанры в очищенном наборе',Counter(r['genre'] for r in clean),'По 6 карточек на жанр. Баланс создан генератором и не доказывает репрезентативность реального архива.')
    chart('02_styles','Стили в очищенном наборе',Counter(r['style'] for r in clean),'По 18 карточек. Простая граница по числу фигур не переносится автоматически на реальный дизайн.')
    chart('03_splits','Объекты в трёх выборках',Counter(r['split'] for r in clean),'По 12 карточек. Дополнительно требуется проверка авторов и хешей, одних размеров выборок недостаточно.')
    with (RESULTS/'exclusions.csv').open(encoding='utf-8',newline='') as stream:
        reasons=Counter(row['reason'] for row in csv.DictReader(stream))
    names={'duplicate_image':'Дубликат','unknown_rights':'Неизвестный допуск','empty_description':'Пустое описание'}
    chart('04_exclusions','Причины исключения записей',{names[k]:v for k,v in reasons.items()},f'От raw {len(raw)} к clean {len(clean)}. Причины взаимоисключающие из-за фиксированного порядка проверок.')
    chart('05_sizes','Размеры учебных макетов',Counter(f"{r['width']} x {r['height']}" for r in clean),'Две группы по 18. Размер полностью связан со стилем в генераторе и не должен становиться скрытым признаком качества.')
    chart('06_missing','Проблемы исходных метаданных',{'Пустое описание':sum(not r['description'] for r in raw),'Неизвестный допуск':sum(r['rights_status']=='unknown' for r in raw)},'Даже небольшой процент пропусков требует решения о допуске; неизвестный статус не следует автоматически заменять разрешённым.')
    save_json(RESULTS/'eda_charts.json',charts)
    save_csv(RESULTS/'eda_summary.csv',[{'figure':c['name'],'finding':c['interpretation']} for c in charts])
    print('Created 6 SVG charts in demo/results/figures')

if __name__=='__main__': run()
