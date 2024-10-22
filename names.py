from random import choice
import logging
log = logging.getLogger(__name__)

adjectives_m = [
    "восхитительный", "енотовидный", "несусветный", "пупырчатый", "прекрасный", "зазнавшийся", "вредный", "упоротый",
    "нежный", "сладкий", "танцующий", "дотошный", "пархающий", "огнедышащий", "ворчливый", "опасный", "зубастый",
    "чертыхающийся", "мягкий", "липкий", "брутальный", "волосатый", "косолапый", "шустрый", "колючий", "прыгучий",
    "косой", "остроухий", "пучеглазый", "милопопый", "упоротый", "железненький", "жирненький", "вяленый", "пятнистый",
    "самый низкий", "гигантский", "сексуальненький", "взорванный", "ленящийся", "кабачковый", "кухонный",
    "афроамериканский", "красный", "медовый", "вафельный", "утончённый", "биполярненький"
]

nouns_m = [
    "пирожок", "кафель", "ёжик", "сандаль", "вафель", "хомяк", "индюшень", "кактус", "мурчень", "топинамбур",
    "лабропудель", "пусикэт", "колобок", "печенько", "котякула", "лень-тюлень", "тюфель", "кабачок", "помидор",
    "птеродактиль", "парадокс", "апофеоз", "крендель", "канделябр", "дирижабль", "усик", "пусик", "пуфик",
    "пельмеш", "бородуль", "вреднозавр", "лапуль", "маффин", "редис", "огурчик", "куксень", "кусь", "сервелат",
    "паштет", "бананчик", "йогуртушка", "зло", "добро", "вантуз", "конь-огонь", "ганглий", "гусищще"
]

adjectives_f = [
    "енотовидная", "восхитительная", "надоедливая", "пупырчатая", "переменчивая", "желанная", "волосатая", "фруктовая",
    "мокренькая", "еловая", "нежная", "загадочная", "голодная", "прожорливая", "сонная", "бодренькая",
    "самодостаточная", "находчивая", "заносчивая", "опасная", "сладострастная", "самобытная", "парнокопытная",
    "колючая", "карманная", "фиолетовая", "жёсткая", "высокогорная", "атмосферная", "тягучая", "упоротая", "жирненькая",
    "сексуальная", "кабачковая", "туалетная", "оранжевая", "белая", "афроамериканская", "медовая", "заводящая",
    "знаменитая", "ежевичная", "клубничная", "вафельная", "чистейшая", "биполярная"
]

nouns_f = [
    "лапка", "жопочка", "совушка", "помидорка", "почемучка", "хвастулька", "селёдонька", "какуленька", "кастрюленька",
    "безешка", "сарделька", "морковка", "катастрофа", "бедулька", "пташка", "тарталетка", "лама", "каналья", "тушка",
    "тученька", "капибара", "кутикула", "вредикула", "убивакула", "обижакула", "канителька", "липученька", "кучка",
    "апельсинушка", "ушная палочка", "клячка", "сручка", "клюшка", "йогуртушка", "зло", "добро", "клякса", "тарелонька",
    "коровья помадка", "улитушка", "гусынюшка", "табуретонька", "индюшатинка"
]


def get_name(available_names=None):
    if not available_names:
        return get_random_name()
    else:
        name = get_random_name()
        while name in available_names:
            log.info(f"Reactivate name generator {name}")
            name = get_random_name()
        return name


def get_random_name():
    if choice([True, False]):
        name = f"{choice(adjectives_m)} {choice(nouns_m)}".title()
        return name
    else:
        name = f"{choice(adjectives_f)} {choice(nouns_f)}".title()
        return name
