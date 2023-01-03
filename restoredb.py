import json
from collections import namedtuple, Counter
import re
import sqlite3
import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


with open('result.json', encoding='utf8') as f:
    jsonfile = json.load(f)

Info = namedtuple('Info', 'id group')

rows = []
added = set()
for row in reversed(jsonfile['messages']):
    if len(row['text']) == 0:
        continue
    t = row['text'][0]

    if isinstance(t, str):
        continue
    #
    # if t['type'] == 'mention' or t['type'] == 'bot_command' or t['type'] == 'phone':
    #     continue

    if t['type'] == 'mention':
        id = t['text']
    elif t['type'] == 'mention_name':
        id = t['user_id']
    else:
        continue

    group_t = row['text'][1]
    if 'відключив' in group_t:
        continue

    assert 'підключив' in group_t, row['text']

    found = re.search(r'до (\d+) групи', group_t)

    if id not in added:
        rows.append(Info(id=id, group=int(found.group(1))))
        added.add(id)
    # print(t)


print(Counter(type(row.id) for row in rows))

print(rows[:10])
print(len(rows))

def connect_db():
    connect = sqlite3.connect('restoreddb.db')
    return connect

connect = connect_db()
cursor = connect.cursor()

username2id = {'@dariusukraine': 880691612, '@ivanna989': 5494531207, '@olehmisar': 524414342, '@vikkkitorii': 544505070, '@MoyAngelochekI': 535448021, '@Novikova_Ganna': 927518754, '@Master_3DPlayYt': 1049082814, '@Zeus2357': 983484162, '@OksankaSmetanka': 5122707921, '@Diablo1206': 1544332060, '@Kengyry17': 808715126, '@bykaal': 941406927, '@blnqw': 1984086740, '@Ania_221': 1493833785, '@Nikola1948': 478223622, '@DmytroKukharenko': 267586116, '@hannaivanchuk': 745607991, '@Denis27072007': 922466516, '@killedbyfrog': 1595724679, '@v_kitral': 953693720, '@vlad_kuk': 1890636137, '@lilsoloman_dra': 996364717, '@sofiykajuras': 965439969, '@anely_14': 5799873081, '@upiterraha': 5300685183, '@Vlad_Tsepesh_III': 372856384, '@RHCP1111962': 5968419555, '@diana_poliak': 827923915, '@Toma_Sankara': 1798085627, '@siergiusz': 1, '@ptocto_akk12': 1638585298, '@mawieqb': 912271752, '@A_l_iic_e': 1940612666, '@verumYAGICH': 582190615, '@kanfetka_04': 666637852, '@LenaVereschagina': 1003092761, '@iru_na': 5097266791, '@Gogigonzik': 1476015856, '@Hrustuna43': 2035326826, '@Ed_bb_b': 1040842206, '@Na_talja': 428691950, '@AndriySamchuk': 82868897, '@choluk': 5950581567, '@yulia_rokunets': 464953231, '@nastitaa': 459968530, '@Maksumi45_4': 944362958, '@Websterrrr': 949742955, '@derskuf': 941406927, '@anassteisha07': 1445480823, '@uras773': 580550628, '@li3rkowalko': 5667139161, '@ziziwug': 909051582, '@zindayra': 869893551, '@sspaceodddity': 735542481, '@vanesamolotkovska': 867003135, '@yanochkaaaaa': 200131680, '@Dmytro727': 943476990, '@yuraturr': 456979469, '@insajder2020': 1095714924, '@None': 0}

print([row.id for row in rows if isinstance(row.id, str)])

for row in rows:
    if isinstance(row.id, str):
        id = username2id[row.id]
    else:
        id = row.id

    cursor.execute("INSERT OR IGNORE INTO database (user_id, group_number) VALUES(?, ?)", (id, row.group))

connect.commit()
