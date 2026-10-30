"""Build individual manuals and export the fully worked artifacts from their source.

Authoring dependencies: python-docx and Pillow. The student demo uses stdlib only.
Run from repository root after python -m demo.project run and python -m demo.eda.
"""
from __future__ import annotations
import ast
import csv
import hashlib
import json
import re
import textwrap
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from PIL import Image, ImageDraw, ImageFont
from draw_diagrams import draw_all

ROOT=Path(__file__).resolve().parents[1]
REPO='https://github.com/Irina-64/ml-creative-technologies-course'
ASSETS=ROOT/'assets'; ASSETS.mkdir(exist_ok=True)
FONT=Path('C:/Windows/Fonts/arial.ttf')
BOLD=Path('C:/Windows/Fonts/arialbd.ttf')

def manual_filename(n):
    return 'МУ_ЛР_09_финал.docx' if n==9 else f'МУ_ЛР_{n:02d}.docx'

# Each item corresponds one-to-one to a required submission artifact.
COVERAGE={
1:[('Project Brief на 2–3 страницы','project_brief.docx'),('Карта стейкхолдеров','stakeholders.md'),('Схема as-is / to-be','scenarios.md'),('Сравнение альтернатив','alternatives.md'),('Ссылка на репозиторий',REPO)],
2:[('Протокол извлечения знаний','protocol.md'),('Обезличенные заметки','notes.md'),('Глоссарий','glossary.md'),('Диаграмма сущностей','entities.md'),('Журнал происхождения','provenance.md')],
3:[('RACI','raci.md'),('Backlog историй','user_stories.md'),('Трассировка','traceability.md'),('Перечень требований','requirements.md'),('Дерево показателей и критерий отказа','requirements.md')],
4:[('Реестр данных','sources.md'),('Data Card v1','data_card.md'),('Схема данных','schema.md'),('Стратегия split','split_and_plan.md'),('Черновик разметки','split_and_plan.md'),('План B','split_and_plan.md')],
5:[('Воспроизводимый скрипт','../../../demo/eda.py'),('Шесть визуализаций','../../../demo/results/figures'),('Таблица качества','quality_review.md'),('Обновлённая Data Card','data_card_update.md')],
6:[('Инструкция разметчика','annotation_guideline.md'),('Версия набора','../../../demo/data/clean.json'),('Статистика разметки','annotation_results.md'),('Проверка согласия','annotation_results.md'),('Код предобработки','../../../demo/project.py')],
7:[('Код baseline','../../../demo/project.py'),('README с запуском','baseline_readme.md'),('Настройки','settings.md'),('Таблица метрик','../../../demo/results/validation_baseline.csv'),('Удачные и ошибочные случаи','baseline_findings.md')],
8:[('Спецификация метрик','metric_spec.md'),('Baseline по сегментам','error_taxonomy.md'),('Таксономия ошибок','error_taxonomy.md'),('Вывод и следующая гипотеза','hypothesis.md')],
9:[('Карточка гипотезы','experiment_plan.md'),('Журнал эксперимента','experiment_log.md'),('Конфигурация запуска','experiment_plan.md'),('Сравнительная таблица','comparison.md'),('Интерпретация и решение','decision.md')],
10:[('Матрица выбора','architecture_matrix.md'),('Архитектурная схема','architecture.md'),('Инструменты и роли','architecture_decision.md'),('Решение и допущения','architecture_decision.md')],
11:[('Запускаемый модуль','../../../demo/server.py'),('Контракт','contract.md'),('Примеры входов и выходов','../../../demo/results/api_examples.json'),('Сложные случаи','cases.md'),('README','module_readme.md'),('Конфигурация без секретов','../../../demo/config.json')],
12:[('Схема потока','feedback_protocol.md'),('Прототип API','../../../demo/server.py'),('Слой знаний','knowledge_layer.md'),('Протокол обратной связи','feedback_protocol.md'),('Исправление и отказ','correction_and_escalation.md')],
13:[('Alpha API','../../../demo/server.py'),('Сценарий показа','walkthrough.md'),('Запись демонстрации','../../../demo/results/walkthrough.cast'),('Инструкция запуска','run_and_record.md'),('Известные ограничения','limitations.md')],
14:[('Model Card v1','model_card.md'),('Реестр рисков','risk_register.md'),('Примеры ограничений','failure_examples.md'),('Принятые меры и открытые риски','mitigations.md')],
15:[('Протокол исследования','research_protocol.md'),('Обезличенные заметки симуляции','simulated_notes.md'),('Сводка результатов','research_findings.md'),('Backlog с приоритетами','research_findings.md'),('Обновлённые документы','documentation_update.md')],
16:[('Презентация','Защита_демо.pptx'),('Ссылка на репозиторий',REPO),('Пакет ЛР 1–15','portfolio.md'),('Alpha и запись','../../../demo/results/walkthrough.cast'),('Индивидуальные карты','contribution_examples.md')]
}
EVIDENCE={
1:['Первый раздел Project Brief','Раздел о ценности и измерении времени','Сравнение альтернатив и выбор TF-IDF со словарём','Раздел о границах alpha'],
2:['Журнал K1–K5 и ссылки на записи','Глоссарий из 18 определений с примерами','Статусы гипотез и отклонённого K4','Связь K1 с R3, K2 с экспериментом, K5 с разметкой'],
3:['Истории R1–R5 содержат роль, действие и пользу','Трассировка связывает источник, проверку и файл','Раздельные продуктовые и технические показатели'],
4:['Реестр и объяснение статуса demo_allowed','Маркер synthetic и описание генератора','Таблица групп и тест пересечений','Ограничения Data Card в основном тексте'],
5:['Две команды и полный скрипт EDA','Шесть подписанных графиков и выводы','Решения об исключении и ограничении признаков','Открыто показаны D001, X001, X003'],
6:['Инструкция, границы и примеры','Детерминированный код и проверки','Два расхождения с сохранёнными метками','IDF только train, тест неизменности'],
7:['Команда и повторный детерминированный запуск','Baseline без дополнительного словаря','NDCG и Recall соответствуют ранжированию','Все 12 случаев, включая шесть неудачных'],
8:['Отдельные сегменты и их объёмы','Таксономия с примерами и проверяемой причиной','H1 следует из неизвестных токенов'],
9:['Меняется только нормализация запроса','Версии, хеш и команда','Ограничение синтетического идеального результата','Критерий отказа и сохранение всех результатов'],
10:['Обязательные ограничения и связь с R','Измеренные оценки отделены от допущений','Один сценарий для трёх альтернатив','Локальность и baseline как plan B'],
11:['Явный контракт и JSON-поля','Сохранённые фактические ответы','Негативные входы и HTTP 400','Полные команды и отсутствие API-ключей'],
12:['Выбор и правка создают события','Версия словаря и происхождение K','No_matches, pending_review и границы полномочий'],
13:['Сценарий заканчивается выбором','Реальный контролируемый fallback','Скрипт записи реальных HTTP-вызовов','Открыто указаны ограничения localhost'],
14:['Конкретные запросы и проверочные команды','Реестр содержит владельца и действие','Версия системы и её фактические результаты','Прямо перечислены запреты'],
15:['Walkthrough не выдаётся за доказательство рынка','Коды U1–U4 и минимизация данных','Наблюдения, интерпретации и решения разделены','Приоритет связан с ущербом и свидетельством'],
16:['Навигация связывает все 15 работ','Запись показывает запрос, выбор и отказ','Карты требуют собственного изменения и объяснения','Слайд ограничений и конкретный следующий эксперимент']}

def source_labs():
    if not (ROOT.parent/'build_lab_guidelines.py').exists():
        return json.loads((ROOT/'source_prompts/requirements.json').read_text(encoding='utf-8'))
    tree=ast.parse((ROOT.parent/'build_lab_guidelines.py').read_text(encoding='utf-8'))
    labs=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LABS' for t in n.targets))
    source=Document(ROOT.parent/'Методические_указания_ЛР_1_16_семестр_3_пошаговые_демо.docx')
    folder=ROOT/'source_prompts'; folder.mkdir(exist_ok=True)
    current=None; blocks={}
    for para in source.paragraphs:
        match=re.match(r'Лабораторная работа (\d+)\.',para.text)
        if match: current=int(match.group(1)); blocks[current]=[]
        elif para.text.startswith('Приложение'): current=None
        if current: blocks[current].append(para.text)
    assert len(blocks)==16
    for n,lines in blocks.items():
        (folder/f'{n:02d}.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    (folder/'requirements.json').write_text(json.dumps(labs,ensure_ascii=False,indent=2),encoding='utf-8')
    return labs

def md_table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']+['| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in row)+' |' for row in rows])

def draw_charts():
    for c in json.loads((ROOT/'demo/results/eda_charts.json').read_text(encoding='utf-8')):
        width=1200; height=125+65*len(c['labels'])
        im=Image.new('RGB',(width,height),'white'); d=ImageDraw.Draw(im)
        titlefont=ImageFont.truetype(str(BOLD),27); font=ImageFont.truetype(str(FONT),23)
        d.text((30,20),c['title'],font=titlefont,fill='black')
        maximum=max(c['values']) or 1
        for i,(label,value) in enumerate(zip(c['labels'],c['values'])):
            y=78+65*i; end=410+int(650*value/maximum)
            d.text((30,y+4),str(label),font=font,fill='black'); d.rectangle((410,y,end,y+35),fill='#2563A6')
            d.text((end+12,y+3),str(value),font=font,fill='black')
        d.text((410,height-35),'Количество карточек',font=ImageFont.truetype(str(FONT),19),fill='#555555')
        im.save(ASSETS/f"{c['name']}.png")

def record_gif():
    records=json.loads((ROOT/'demo/results/walkthrough.json').read_text(encoding='utf-8'))
    frames=[]
    font=ImageFont.truetype(str(FONT),23); titlefont=ImageFont.truetype(str(BOLD),31)
    for r in records:
        im=Image.new('RGB',(1200,720),'#F7F9FB'); d=ImageDraw.Draw(im)
        d.text((45,35),r['case'],font=titlefont,fill='black')
        body=r['output']
        lines=[f"POST {r['path']}",json.dumps(r['input'],ensure_ascii=False),f"HTTP {r['http_status']}   status = {body.get('status')}"]
        if 'results' in body:
            lines+= [f"model = {body.get('model')}"]
            lines += [f"{x['id']}   {x['genre']}   {x['style']}   score {x['score']}" for x in body['results']]
            lines+= ['Источник и допуск переданы в JSON. Решение остаётся за человеком.']
        else: lines += [json.dumps(body,ensure_ascii=False)]
        y=110
        for line in lines:
            for part in textwrap.wrap(line, width=78):
                d.text((45,y),part,font=font,fill='#152A40'); y+=36
        d.text((45,650),'Фактические HTTP-ответы. Анимированный повтор записи, не пользовательское исследование.',font=ImageFont.truetype(str(FONT),20),fill='#555555')
        frames.append(im)
    frames[0].save(ROOT/'demo/results/walkthrough.gif',save_all=True,append_images=frames[1:],duration=6000,loop=0)

def render_doc(text,path):
    doc=Document(); sec=doc.sections[0]
    for style in doc.styles:
        for border in list(style._element.iter(qn('w:pBdr'))):
            border.getparent().remove(border)
    sec.page_width=Inches(8.5); sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Cm(1.8); sec.left_margin=Cm(2.1); sec.right_margin=Cm(1.8)
    for name,size in [('Normal',11),('Title',19),('Heading 1',15),('Heading 2',12),('Heading 3',11)]:
        style=doc.styles[name]; style.font.name='Arial'; style.font.size=Pt(size); style.font.color.rgb=RGBColor(0,0,0)
        style._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Arial')
        style.paragraph_format.space_after=Pt(6); style.paragraph_format.line_spacing=1.08
        if name!='Normal': style.font.bold=True; style.paragraph_format.keep_with_next=True; style.paragraph_format.space_before=Pt(10)
    doc.core_properties.title=text.splitlines()[0].lstrip('# ')
    doc.core_properties.subject='Методические указания и полный учебный демо-вариант'
    doc.core_properties.author='Учебные материалы курса'
    lines=text.splitlines(); i=0; first=True
    while i<len(lines):
        line=lines[i].strip()
        if not line or line.startswith('<!--'): i+=1; continue
        if line=='[[PAGEBREAK]]': doc.add_page_break(); i+=1; continue
        if line.startswith('```'):
            code=[]; i+=1
            while i<len(lines) and not lines[i].startswith('```'): code.append(lines[i]); i+=1
            for code_line in code:
                for wrapped in textwrap.wrap(code_line,width=94,replace_whitespace=False,drop_whitespace=False) or ['']:
                    para=doc.add_paragraph(); para.paragraph_format.space_after=Pt(0)
                    para.paragraph_format.line_spacing=1.0
                    run=para.add_run(wrapped); run.font.name='Consolas'; run.font.size=Pt(9)
            doc.add_paragraph(); i+=1; continue
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].strip().startswith('|'): block.append(lines[i].strip()); i+=1
            data=[[v.strip() for v in row.strip('|').split('|')] for row in block if not re.fullmatch(r'[|\s:\-]+',row)]
            if not data: continue
            columns=len(data[0]); table=doc.add_table(rows=1,cols=columns); table.alignment=WD_TABLE_ALIGNMENT.CENTER; table.autofit=False
            available=17.69
            # Text-heavy fields receive more space than identifiers and numeric metrics.
            weights=[max(6,min(30,max(len(row[c]) if c<len(row) else 0 for row in data))) for c in range(columns)]
            if columns==6: weights=[6,25,7,7,14,7]
            widths=[available*w/sum(weights) for w in weights]
            for c,w in zip(table.columns,widths): c.width=Cm(w)
            for ri,row in enumerate(data):
                cells=table.rows[0].cells if ri==0 else table.add_row().cells
                for ci,(cell,value) in enumerate(zip(cells,row)):
                    cell.width=Cm(widths[ci]); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    cell.text=value.replace('`','')
                    for para in cell.paragraphs:
                        para.paragraph_format.space_after=Pt(3); para.paragraph_format.space_before=Pt(3); para.paragraph_format.line_spacing=1.03
                        if ri==0: para.paragraph_format.keep_with_next=True
                        for run in para.runs: run.font.name='Arial'; run.font.size=Pt(9); run.bold=ri==0
                    pr=cell._tc.get_or_add_tcPr()
                    borders=OxmlElement('w:tcBorders')
                    for side in ('top','left','bottom','right'):
                        el=OxmlElement('w:'+side); el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'4'); el.set(qn('w:color'),'D9D9D9'); borders.append(el)
                    pr.append(borders)
                    margins=OxmlElement('w:tcMar')
                    for side in ('top','bottom','left','right'):
                        el=OxmlElement('w:'+side); el.set(qn('w:w'),'70'); el.set(qn('w:type'),'dxa'); margins.append(el)
                    pr.append(margins)
                    if ri==0:
                        shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'E7EEF6'); pr.append(shade)
                trpr=table.rows[ri]._tr.get_or_add_trPr()
                no_split=OxmlElement('w:cantSplit'); trpr.append(no_split)
                if ri==0: trpr.append(OxmlElement('w:tblHeader'))
            doc.add_paragraph(); continue
        match=re.match(r'!\[(.*?)\]\((.*?)\)',line)
        if match:
            image_path=(path.parent/match.group(2)).resolve()
            if not image_path.exists(): image_path=ROOT/match.group(2)
            doc.add_picture(str(image_path),width=Cm(16.5))
            caption=doc.add_paragraph(match.group(1)); caption.paragraph_format.space_after=Pt(8)
            for run in caption.runs: run.font.size=Pt(9)
            i+=1; continue
        if line.startswith('#'):
            m=re.match(r'(#+)\s+(.*)',line); level=len(m[1]); title=m[2]
            if first:
                doc.add_paragraph(title,style='Title'); first=False
            else: doc.add_heading(title,level=min(level,3))
            i+=1; continue
        if re.match(r'^\d+\. ',line):
            para=doc.add_paragraph(line)
            para.paragraph_format.keep_with_next=not line.startswith('6. ')
            i+=1; continue
        paragraph=[]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','<!--','![','[[PAGEBREAK]]')) and not re.match(r'^\d+\. ',lines[i]):
            paragraph.append(lines[i].strip()); i+=1
        if not paragraph: i+=1; continue
        para=doc.add_paragraph()
        for j,part in enumerate(re.split(r'(`[^`]+`)', ' '.join(paragraph))):
            run=para.add_run(part.strip('`') if part.startswith('`') else part)
            if part.startswith('`'): run.font.name='Consolas'; run.font.size=Pt(10)
    path.parent.mkdir(parents=True,exist_ok=True); doc.save(path)

def substitute(text,n):
    captions={'scenario_flow':'Схема текущего и целевого сценариев','entity_map':'Диаграмма сущностей и связей','metrics_tree':'Дерево показателей','architecture_flow':'Архитектурная схема alpha','feedback_flow':'Схема обратной связи'}
    text=re.sub(r'\{\{figure:(.*?)\}\}',lambda m:f'![{captions.get(m[1],m[1])}](../../assets/{m[1]}.png)',text)
    def csv_sub(m):
        with (ROOT/m[1]).open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        keys=['query_id','query','ndcg','recall','returned','grades']
        return md_table(['ID','Запрос','NDCG','Recall','Выдача','Grades'],[[r[k] for k in keys] for r in rows])
    text=re.sub(r'\{\{csv:(.*?)\}\}',csv_sub,text)
    if '{{api_examples}}' in text:
        examples=json.loads((ROOT/'demo/results/api_examples.json').read_text(encoding='utf-8'))
        first=examples[1]
        value='Полный ответ на известный синонимический запрос:\n\n```json\n'+json.dumps(first,ensure_ascii=False,indent=2)+'\n```\n\n'
        value+=md_table(['Случай','HTTP','Статус или ошибка','Результат'],[[r['case'],r['http_status'],r['output'].get('error',r['output'].get('status')),' '.join(x['id'] for x in r['output'].get('results',[])) or 'Пустой список / ошибка'] for r in examples])
        text=text.replace('{{api_examples}}',value)
    if '{{walkthrough}}' in text:
        records=json.loads((ROOT/'demo/results/walkthrough.json').read_text(encoding='utf-8'))
        text=text.replace('{{walkthrough}}',md_table(['Шаг','Путь','HTTP','Фактический ответ'],[[r['case'],r['path'],r['http_status'],str(r['output'].get('status'))+': '+(', '.join(x['id'] for x in r['output'].get('results',[])) or r['output'].get('error', 'пустой список' if 'results' in r['output'] else 'событие сохранено'))] for r in records]))
    return text

def build(only=None):
    labs=source_labs(); draw_charts(); draw_all(); record_gif()
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8')) if only and (ROOT/'manifest.json').exists() else []
    if only:
        labs=[lab for lab in labs if lab['n'] in only]
        manifest=[row for row in manifest if row['lab'] not in only]
    for lab in labs:
        n=lab['n']; directory=ROOT/'labs'/f'{n:02d}'; demo=directory/'demo'; demo.mkdir(parents=True,exist_ok=True)
        method=(ROOT/'content'/f'{n:02d}_method.md').read_text(encoding='utf-8')
        example=(ROOT/'content'/f'{n:02d}_demo.md').read_text(encoding='utf-8')
        assert len(re.findall(r'### Шаг \d',method))==6
        for name,body in re.findall(r'<!-- artifact: (.*?) -->\s*(.*?)\s*<!-- endartifact -->',example,re.S):
            artifact_text=substitute(body,n).replace('../../assets/','../../../assets/').replace('[[PAGEBREAK]]','<!-- Page break in Word version -->')
            (demo/name).write_text(artifact_text+'\n',encoding='utf-8')
            if n==1 and name=='project_brief.md': render_doc(body,demo/'project_brief.docx')
        title=re.sub(r'[:/,]',' ',lab['title']).replace('  ',' ')
        prefix=f'# Лабораторная работа {n}\n\n## {title}\n\nМетодические указания по дисциплине «Проект — применение машинного обучения в креативных технологиях». Магистратура, второй курс, первый семестр курса (третий семестр обучения).\n\nСвязь с лекциями: {lab["lectures"]}. Компетенции и индикаторы: {lab["competencies"]}.\n\n## Цель\n\n{lab["goal"]}\n\n## Исходная ситуация\n\n{lab["context"]}\n\n'
        handoff=f'Вход для работы: '+('согласуемая идея проекта.' if n==1 else f'артефакты предыдущих работ, прежде всего ЛР {n-1}.')+' Результат включается в портфолио и используется на следующих шагах.\n\n'
        source_steps='## Исходные шесть требований к выполнению\n\n'+'\n\n'.join(f'{i}. {t}' for i,t in enumerate(lab['steps'],1))+'\n\n'
        # The original requirements are retained verbatim; expanded steps explain how to execute them.
        text=prefix+handoff+method+'\n\n'+substitute(example,n)+'\n\n'
        text+='## Что сдать\n\n'+lab['deliverables']+'\n\n'
        text+='Пути ниже указаны относительно папки demo данной ЛР, если не приведён полный адрес.\n\n'
        text+=md_table(['Требуемый материал','Где находится выполненный образец'],COVERAGE[n])+'\n\n'
        text+='## Критерии приёмки\n\n'+lab['acceptance']+'\n\n'
        criteria=[c.strip().rstrip('.') for c in lab['acceptance'].split(';')]
        assert len(criteria)==len(EVIDENCE[n]),(n,criteria,EVIDENCE[n])
        text+=md_table(['Критерий','Свидетельство в демо'],zip(criteria,EVIDENCE[n]))+'\n\n'
        text+='## Типичные ошибки\n\n'+lab['mistakes']+'\n\n## Самопроверка перед сдачей\n\n'+lab['selfcheck']+'\n\n'
        text+='На индивидуальной защите объясните одно своё решение, покажите его артефакт и назовите ограничение. Учебный демо-вариант служит образцом оформления; собственный проект требует собственных данных, решений и подтверждённого вклада.\n\n'
        text+='## Материалы и источники\n\n'+REPO+f'/tree/main/labs/{n:02d}\n\nИсходное задание сохранено в source_prompts/{n:02d}.md. Формулировки компетенций приведены в COURSE_BASIS.md.\n\n'
        if n in (7,8,9,10,11):
            text+='TF-IDF и текстовые признаки: https://scikit-learn.org/stable/modules/feature_extraction.html. Метрики ранжирования: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html. В демо явно задан экспоненциальный gain; библиотечные соглашения могут отличаться.\n\n'
        if n in (11,12,13): text+='Документация локального HTTP-сервера Python: https://docs.python.org/3/library/http.server.html. Этот сервер предназначен здесь только для учебного запуска на localhost.\n\n'
        text+=source_steps
        text=re.sub(r'<!--.*?-->','',text,flags=re.S)
        (directory/'README.md').write_text(text.replace('[[PAGEBREAK]]',''),encoding='utf-8')
        docx=directory/manual_filename(n); render_doc(text,docx)
        manifest.append({'lab':n,'title':lab['title'],'docx':str(docx.relative_to(ROOT)).replace('\\','/'),'words':len(text.split()),'required_artifacts':len(COVERAGE[n]),'artifact_files':[str(p.relative_to(ROOT)).replace('\\','/') for p in demo.glob('*')]})
    manifest.sort(key=lambda row:row['lab'])
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{'lab':r['lab'],'words':r['words'],'artifacts':r['required_artifacts']} for r in manifest],ensure_ascii=False,indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--labs',nargs='+',type=int)
    build(parser.parse_args().labs)
