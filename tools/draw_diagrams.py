"""Editable diagram definitions; raster output for portable Word/GitHub viewing."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
FONT = 'C:/Windows/Fonts/arial.ttf'
BOLD = 'C:/Windows/Fonts/arialbd.ttf'

def diagram(name, title, nodes, edges, height=620):
    im=Image.new('RGB',(1500,height),'white'); d=ImageDraw.Draw(im)
    font=ImageFont.truetype(FONT,25); small=ImageFont.truetype(FONT,22)
    d.text((30,20),title,font=ImageFont.truetype(BOLD,32),fill='#152A40')
    for source,target,label in edges:
        a=nodes[source]; b=nodes[target]
        ax,ay,aw,ah=a[:4]; bx,by,bw,bh=b[:4]
        if name!='metrics_tree' and abs((bx+bw/2)-(ax+aw/2))>abs((by+bh/2)-(ay+ah/2)):
            start=(ax+aw if bx>ax else ax,ay+ah/2); end=(bx if bx>ax else bx+bw,by+bh/2)
        else:
            start=(ax+aw/2,ay+ah if by>ay else ay); end=(bx+bw/2,by if by>ay else by+bh)
        d.line([start,end],fill='#52677C',width=3)
        ang=math.atan2(end[1]-start[1],end[0]-start[0])
        d.polygon([end,(end[0]-15*math.cos(ang-.45),end[1]-15*math.sin(ang-.45)),(end[0]-15*math.cos(ang+.45),end[1]-15*math.sin(ang+.45))],fill='#52677C')
        if label:
            mx=(start[0]+end[0])/2; my=(start[1]+end[1])/2
            box=d.textbbox((0,0),label,font=small); tw=box[2]-box[0]
            d.rectangle((mx-tw/2-6,my-29,mx+tw/2+6,my-3),fill='white')
            d.text((mx-tw/2,my-29),label,font=small,fill='#152A40')
    for x,y,w,h,label in nodes.values():
        d.rectangle((x,y,x+w,y+h),fill='#EEF4FA',outline='#6D859D',width=2)
        lines=label.split('\n'); total=31*len(lines)
        for i,line in enumerate(lines):
            box=d.textbbox((0,0),line,font=font); tw=box[2]-box[0]
            d.text((x+(w-tw)/2,y+(h-total)/2+i*31),line,font=font,fill='#152A40')
    im.save(ROOT/'assets'/f'{name}.png')

def draw_all():
    diagram('scenario_flow','Текущий и целевой сценарии',{
      'a':(30,100,230,90,'Бриф'), 'b':(350,100,290,90,'Просмотр папок'),
      'c':(740,100,300,90,'Проверка источника'), 'd':(1140,100,320,90,'Выбор дизайнера'),
      'e':(30,330,230,90,'Бриф / запрос'), 'f':(350,330,290,90,'Поиск и допуск'),
      'g':(740,330,300,90,'Карточки с\nисточниками'), 'h':(1140,330,320,90,'Выбор / отклонение'),
      'i':(350,500,290,80,'Уточнить запрос'), 'j':(740,500,300,80,'Проверка архивариуса')},
      [('a','b','as-is'),('b','c',''),('c','d',''),('e','f','to-be'),('f','g',''),('g','h',''),('f','i','нет совпадений'),('g','j','спорный допуск')])
    diagram('entity_map','Сущности и кратности связей учебного каталога',{
      'a':(30,100,250,90,'Автор'), 's':(30,290,250,90,'Серия'),
      'c':(530,195,340,110,'Карточка'), 'o':(1170,100,290,90,'Источник'),
      'r':(1170,290,290,90,'Статус допуска'), 'q':(30,490,250,90,'Запрос'),
      'v':(530,490,340,90,'Решение дизайнера'), 'f':(1170,490,290,90,'Событие feedback')},
      [('a','c','1 : N'),('s','c','1 : N'),('c','o','N : 1'),('c','r','N : 1'),('q','c','N : M'),('c','v','1 : N'),('v','f','1 : 0..1')])
    diagram('metrics_tree','Цель, условия успеха и проверяемые показатели',{
      'a':(440,90,620,100,'Обоснованный выбор референса\nдо 5 минут без помощи'),
      'b':(30,300,420,100,'Релевантность\nNDCG@3 ≥ 0,70'),
      'c':(540,300,420,100,'Понятность сценария\nреальный walkthrough'),
      'd':(1050,300,420,100,'Доступность результата\nответ до 10 секунд'),
      'e':(220,510,1060,80,'Защитные условия: неизвестный допуск = 0; Recall@3 ≥ baseline')},
      [('a','b',''),('a','c',''),('a','d',''),('b','e',''),('c','e',''),('d','e','')])
    diagram('architecture_flow','Компоненты alpha и резервный путь',{
      'a':(20,100,270,90,'JSON-запрос'), 'b':(400,100,300,90,'Проверка ввода'),
      'c':(810,100,300,90,'Словарь v1'), 'd':(810,310,300,90,'TF-IDF / train-IDF'),
      'e':(400,310,300,90,'Фильтр допуска'), 'f':(20,310,270,90,'Top-3 JSON'),
      'g':(1170,310,300,90,'Без словаря\nstatus=fallback'), 'h':(20,510,270,80,'Выбор / feedback')},
      [('a','b',''),('b','c',''),('c','d',''),('d','e',''),('e','f',''),('c','g','отказ'),('g','d',''),('f','h','')])
    diagram('feedback_flow','Исправления и эскалации: модель автоматически не меняется',{
      'a':(30,120,300,100,'Правка / эскалация'), 'b':(600,120,300,100,'POST /feedback'),
      'c':(1170,120,300,100,'pending_review'), 'd':(1170,370,300,100,'Проверка человеком'),
      'e':(600,370,300,100,'Новая версия данных'), 'f':(30,370,300,100,'Повторная оценка')},
      [('a','b','correct / escalate'),('b','c','сохранение'),('c','d','вне API alpha'),('d','e','если принято'),('e','f','до выпуска')],height=540)

if __name__=='__main__': draw_all()
