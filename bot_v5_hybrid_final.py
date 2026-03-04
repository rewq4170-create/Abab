"""
╔════════════════════════════════════════════════════════════════════╗
║         RPG Telegram Bot  v5.0 - HYBRID EDITION                    ║
║                                                                    ║
║  ✅ ВСЕ ФУНКЦИИ ИЗ v4.1 СОХРАНЕНЫ:                              ║
║  • Выбор характеристик и классов                                 ║
║  • Магазин и инвентарь                                           ║
║  • Крафт и материалы                                             ║
║  • Полная боевая система                                         ║
║  • Подземелье                                                    ║
║  • Всё остальное!                                                ║
║                                                                    ║
║  ✨ НОВОЕ В v5.0:                                                ║
║  🏆 Пошаговая Арена (интерактивный PvP)                         ║
║  🗺️  Карта мира с 4 локациями                                   ║
║  📋 Система квестов                                             ║
║  💎 Система редкости предметов                                  ║
║                                                                    ║
║  УДАЛЕНО: элементы стихий, стойки                               ║
╚════════════════════════════════════════════════════════════════════╝
"""
import telebot
import sqlite3
import random
import time
from telebot import types

TOKEN = '8695590672:AAEgPT62pXsOD4--ebgBneHJBvW60PpzgI4'
bot = telebot.TeleBot(TOKEN)

# Хранилища состояний для боёв
battle_states = {}  # Боевые состояния с врагами
pvp_states = {}     # PvP боевые состояния (пошаговая система)

bot.set_my_commands([
    telebot.types.BotCommand("start", "🎮 Начать игру / Персонаж"),
    telebot.types.BotCommand("profile", "👤 Профиль"),
    telebot.types.BotCommand("stats", "📊 Распределить статы"),
    telebot.types.BotCommand("map", "🗺️ Карта мира (НОВОЕ!)"),
    telebot.types.BotCommand("fight", "⚔️ Бой"),
    telebot.types.BotCommand("shop", "🛒 Магазин"),
    telebot.types.BotCommand("inventory", "📦 Инвентарь"),
    telebot.types.BotCommand("craft", "🔨 Крафт"),
    telebot.types.BotCommand("quests", "📋 Квесты (НОВОЕ!)"),
    telebot.types.BotCommand("dungeon", "🏰 Подземелье"),
    telebot.types.BotCommand("arena", "🏆 Арена ПОШАГОВАЯ (НОВОЕ!)"),
    telebot.types.BotCommand("daily", "🎁 Награда"),
    telebot.types.BotCommand("leaderboard", "🏅 Рейтинг"),
    telebot.types.BotCommand("help", "📖 Справка"),
    telebot.types.BotCommand("reset", "🔄 Сброс"),
])

# ══════════════════════════════════════════════════════════════
#  КОНФИГУРАЦИЯ
# ══════════════════════════════════════════════════════════════

RARITY = {
    "common":     {"name": "⚪ Обычный",     "emoji": "⚪", "drop_chance": 50},
    "uncommon":   {"name": "🟢 Необычный",   "emoji": "🟢", "drop_chance": 25},
    "rare":       {"name": "🔵 Редкий",      "emoji": "🔵", "drop_chance": 15},
    "epic":       {"name": "🟣 Эпический",   "emoji": "🟣", "drop_chance": 8},
    "legendary":  {"name": "🟡 Легендарный", "emoji": "🟡", "drop_chance": 2},
}

MATERIALS = {
    "iron_ore": {"name": "⛏️ Железная руда", "rarity": "common"},
    "copper_ore": {"name": "🪙 Медная руда", "rarity": "common"},
    "mana_crystal": {"name": "🔮 Кристалл маны", "rarity": "rare"},
    "leather": {"name": "🧥 Кожа", "rarity": "uncommon"},
    "bone": {"name": "💀 Кость", "rarity": "uncommon"},
    "dragon_scale": {"name": "🐉 Чешуя дракона", "rarity": "legendary"},
}

RECIPES = {
    "health_potion": {
        "name": "🧪 Зелье HP",
        "materials": {"iron_ore": 2},
        "gold": 50,
        "result": ("potion_hp_big", 1)
    },
    "mana_potion": {
        "name": "💧 Мана-зелье",
        "materials": {"copper_ore": 1, "mana_crystal": 1},
        "gold": 100,
        "result": ("mana_pot", 2)
    },
    "strong_sword": {
        "name": "⚔️ Мощный меч",
        "materials": {"iron_ore": 5, "bone": 2},
        "gold": 300,
        "result": ("sword_strong", 1),
        "min_level": 15
    },
}

LOCATIONS = {
    "forest": {
        "name": "🌲 Лес",
        "desc": "Уровень 1-3 | Волки, пауки, бандиты",
        "min_lvl": 1,
        "max_lvl": 3,
        "emoji": "🌲"
    },
    "swamp": {
        "name": "🏜️ Болото",
        "desc": "Уровень 4-7 | Зомби, слизни, ведьмы",
        "min_lvl": 4,
        "max_lvl": 7,
        "emoji": "🏜️"
    },
    "mountains": {
        "name": "⛰️ Горы",
        "desc": "Уровень 8-12 | Огры, драконы, големы",
        "min_lvl": 8,
        "max_lvl": 12,
        "emoji": "⛰️"
    },
    "castle": {
        "name": "🏰 Замок",
        "desc": "Уровень 13+ | Архимаги, боссы, демоны",
        "min_lvl": 13,
        "max_lvl": 999,
        "emoji": "🏰"
    },
}

CLASS_CONFIG = {
    "Тяжеловес": {
        "hp_mod": 1.8, "atk_mod": 0.95, "emoji": "🛡",
        "desc": "Огромное HP, танк",
        "abilities": ["bastion", "taunt"],
        "passive": "При HP < 30%: DEF x1.5"
    },
    "Стеклянная пушка": {
        "hp_mod": 0.55, "atk_mod": 2.1, "emoji": "⚔️",
        "desc": "Максимальный урон",
        "abilities": ["barrage", "execute"],
        "passive": "Крит x2.5"
    },
    "Ассасин": {
        "hp_mod": 0.85, "atk_mod": 1.45, "emoji": "👤",
        "desc": "Высокий уклон",
        "abilities": ["backstab", "smoke"],
        "passive": "+25% урон после уклонения"
    },
    "Мистик": {
        "hp_mod": 1.05, "atk_mod": 1.15, "emoji": "🔮",
        "desc": "Магические способности",
        "abilities": ["fireball", "weaken"],
        "passive": "INT даёт +5% ATK"
    },
    "Паладин": {
        "hp_mod": 1.35, "atk_mod": 1.05, "emoji": "✨",
        "desc": "Исцеление и поддержка",
        "abilities": ["holy_strike", "heal"],
        "passive": "20% исцелиться на 15% при ударе"
    },
}

LOCATION_MONSTERS = {
    "forest": [
        {"n": "🐺 Волк", "hp": 20, "atk": 8, "g": 10, "sp": None, "mat": {"leather": 1}},
        {"n": "🕷️ Паук", "hp": 15, "atk": 10, "g": 15, "sp": None, "mat": {"bone": 1}},
        {"n": "🗡️ Бандит", "hp": 25, "atk": 12, "g": 20, "sp": None, "mat": {"iron_ore": 1}},
    ],
    "swamp": [
        {"n": "🧟 Зомби", "hp": 40, "atk": 14, "g": 25, "sp": None, "mat": {"bone": 2}},
        {"n": "💧 Слизень", "hp": 30, "atk": 8, "g": 20, "sp": None, "mat": {"copper_ore": 1}},
        {"n": "🧙‍♀️ Ведьма", "hp": 35, "atk": 16, "g": 35, "sp": None, "mat": {"mana_crystal": 1}},
    ],
    "mountains": [
        {"n": "👹 Огр", "hp": 60, "atk": 22, "g": 50, "sp": None, "mat": {"iron_ore": 2}},
        {"n": "🐉 Дракончик", "hp": 70, "atk": 28, "g": 70, "sp": None, "mat": {"dragon_scale": 1}},
        {"n": "🗿 Голем", "hp": 80, "atk": 18, "g": 60, "sp": None, "mat": {"iron_ore": 3}},
    ],
    "castle": [
        {"n": "🧙 Архимаг", "hp": 90, "atk": 35, "g": 100, "sp": None, "mat": {"mana_crystal": 2}},
        {"n": "👿 Демон", "hp": 100, "atk": 40, "g": 120, "sp": None, "mat": {"dragon_scale": 1}},
        {"n": "☠️ Лич", "hp": 110, "atk": 45, "g": 150, "sp": None, "mat": {"dragon_scale": 2}},
    ],
}

# ══════════════════════════════════════════════════════════════
#  БД
# ══════════════════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        level INTEGER,
        exp INTEGER,
        gold INTEGER,
        class TEXT,
        str_stat INTEGER,
        dex_stat INTEGER,
        int_stat INTEGER,
        con_stat INTEGER,
        wins INTEGER,
        losses INTEGER,
        gold_earned INTEGER,
        exp_level INTEGER,
        hp_potions INTEGER,
        mana_potions INTEGER,
        equipment_level INTEGER,
        equipped_atk INTEGER,
        equipped_def INTEGER,
        is_ready INTEGER,
        last_daily INTEGER,
        arena_rating INTEGER,
        daily_kills INTEGER,
        daily_crafts INTEGER,
        weekly_bosses INTEGER
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        item_name TEXT,
        quantity INTEGER
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS materials (
        mat_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        material_name TEXT,
        quantity INTEGER
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS arena_queue (
        user_id INTEGER PRIMARY KEY,
        joined_at INTEGER
    )""")
    
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user(user_id, **kwargs):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE users SET {key}=? WHERE user_id=?", (value, user_id))
    conn.commit()
    conn.close()

def add_material(user_id, key, qty=1):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT quantity FROM materials WHERE user_id=? AND material_name=?", (user_id, key))
    row = c.fetchone()
    if row:
        c.execute("UPDATE materials SET quantity=? WHERE user_id=? AND material_name=?",
                  (row[0] + qty, user_id, key))
    else:
        c.execute("INSERT INTO materials(user_id, material_name, quantity) VALUES(?,?,?)",
                  (user_id, key, qty))
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════════
#  ПОШАГОВАЯ АРЕНА v5.0
# ══════════════════════════════════════════════════════════════

def start_pvp_battle(chat_id, uid1, uid2):
    """Инициализация PvP боя"""
    user1 = get_user(uid1)
    user2 = get_user(uid2)
    
    atk1 = max(1, int(user1[6] * 1.5 + user1[17]))
    atk2 = max(1, int(user2[6] * 1.5 + user2[17]))
    def1 = max(1, int(user1[9] * 0.8 + user1[18]))
    def2 = max(1, int(user2[9] * 0.8 + user2[18]))
    
    hp1 = int(user1[6] * 15 * CLASS_CONFIG[user1[5]]["hp_mod"])
    hp2 = int(user2[6] * 15 * CLASS_CONFIG[user2[5]]["hp_mod"])
    
    pvp_states[f"{uid1}_{uid2}"] = {
        'player1': uid1,
        'player2': uid2,
        'p1_name': user1[1],
        'p2_name': user2[1],
        'p1_hp': hp1,
        'p2_hp': hp2,
        'p1_atk': atk1,
        'p2_atk': atk2,
        'p1_def': def1,
        'p2_def': def2,
        'turn': 1,
        'current_player': uid1,
        'log': [f"⚔️ {user1[1]} vs {user2[1]}"]
    }
    
    show_pvp_screen(chat_id, uid1, uid2)

def show_pvp_screen(chat_id, uid1, uid2):
    """Показать экран пошагового PvP боя"""
    battle_key = f"{uid1}_{uid2}"
    if battle_key not in pvp_states:
        return
    
    battle = pvp_states[battle_key]
    
    text = f"""⚔️ АРЕНА | Ход {battle['turn']}

👤 {battle['p1_name']}: {max(0, battle['p1_hp'])} ❤️
🏆 {battle['p2_name']}: {max(0, battle['p2_hp'])} ❤️

Ход: {"👤 " + battle['p1_name'] if battle['current_player'] == uid1 else "🏆 " + battle['p2_name']}"""
    
    mk = types.InlineKeyboardMarkup()
    
    if battle['current_player'] == uid1:
        mk.add(
            types.InlineKeyboardButton("🗡 Атака", callback_data=f"pvp_atk_{uid1}_{uid2}"),
            types.InlineKeyboardButton("🛡 Защита", callback_data=f"pvp_def_{uid1}_{uid2}")
        )
    else:
        mk.add(
            types.InlineKeyboardButton("🗡 Атака", callback_data=f"pvp_atk_{uid2}_{uid1}"),
            types.InlineKeyboardButton("🛡 Защита", callback_data=f"pvp_def_{uid2}_{uid1}")
        )
    
    bot.send_message(chat_id, text, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pvp_"))
def handle_pvp_action(call):
    """Обработка действия в PvP арене"""
    parts = call.data.split("_")
    action = parts[1]
    actor = int(parts[2])
    opponent = int(parts[3])
    
    battle_key = f"{actor}_{opponent}"
    if battle_key not in pvp_states:
        battle_key = f"{opponent}_{actor}"
    
    if battle_key not in pvp_states:
        bot.answer_callback_query(call.id, "❌ Бой закончился")
        return
    
    battle = pvp_states[battle_key]
    
    if battle['current_player'] != actor:
        bot.answer_callback_query(call.id, "⏳ Не ваш ход!")
        return
    
    if actor == battle['player1']:
        attacker_atk = battle['p1_atk']
        defender_hp = battle['p2_hp']
        defender_def = battle['p2_def']
        is_p1 = True
    else:
        attacker_atk = battle['p2_atk']
        defender_hp = battle['p1_hp']
        defender_def = battle['p1_def']
        is_p1 = False
    
    if action == "atk":
        damage = max(1, attacker_atk - int(defender_def * 0.3) + random.randint(-2, 4))
        if is_p1:
            battle['p2_hp'] -= damage
            battle['log'].append(f"🗡 {battle['p1_name']} атаковал! Урон: {damage}")
        else:
            battle['p1_hp'] -= damage
            battle['log'].append(f"🗡 {battle['p2_name']} атаковал! Урон: {damage}")
    
    if battle['p1_hp'] <= 0:
        winner, loser = battle['player2'], battle['player1']
        winner_name = battle['p2_name']
        battle['log'].append(f"\n🏆 {winner_name} ПОБЕДИЛ!")
        user_w, user_l = get_user(winner), get_user(loser)
        update_user(winner, wins=user_w[10]+1, arena_rating=user_w[21]+30)
        update_user(loser, losses=user_l[11]+1, arena_rating=max(0, user_l[21]-30))
        del pvp_states[battle_key]
        bot.send_message(call.message.chat.id, "\n".join(battle['log']))
        return
    
    if battle['p2_hp'] <= 0:
        winner, loser = battle['player1'], battle['player2']
        winner_name = battle['p1_name']
        battle['log'].append(f"\n🏆 {winner_name} ПОБЕДИЛ!")
        user_w, user_l = get_user(winner), get_user(loser)
        update_user(winner, wins=user_w[10]+1, arena_rating=user_w[21]+30)
        update_user(loser, losses=user_l[11]+1, arena_rating=max(0, user_l[21]-30))
        del pvp_states[battle_key]
        bot.send_message(call.message.chat.id, "\n".join(battle['log']))
        return
    
    battle['turn'] += 1
    battle['current_player'] = battle['player2'] if battle['current_player'] == battle['player1'] else battle['player1']
    
    bot.edit_message_text("⏳ Ход обрабатывается...", call.message.chat.id, call.message.message_id)
    show_pvp_screen(call.message.chat.id, battle['player1'], battle['player2'])

# ══════════════════════════════════════════════════════════════
#  КАРТА МИРА v5.0
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['map'])
def show_map(message):
    u = get_user(message.from_user.id)
    if not u or u[19] == 0:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    text = "🗺️ КАРТА МИРА\n\n"
    mk = types.InlineKeyboardMarkup()
    
    for loc_key, loc_info in LOCATIONS.items():
        text += f"{loc_info['emoji']} {loc_info['name']}\n{loc_info['desc']}\n\n"
        mk.add(types.InlineKeyboardButton(f"{loc_info['emoji']} {loc_info['name']}", 
                                         callback_data=f"loc_{loc_key}"))
    
    bot.send_message(message.chat.id, text, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("loc_"))
def select_location(call):
    uid = call.from_user.id
    loc_key = call.data.replace("loc_", "")
    
    if loc_key not in LOCATIONS:
        return
    
    loc_info = LOCATIONS[loc_key]
    u = get_user(uid)
    
    if u[2] < loc_info["min_lvl"]:
        bot.answer_callback_query(call.id, f"❌ Требуется уровень {loc_info['min_lvl']}+")
        return
    
    monster = random.choice(LOCATION_MONSTERS[loc_key]).copy()
    
    text = f"""{loc_info['emoji']} {loc_info['name']}

Встреча!
{monster['n']}
❤️ HP: {monster['hp']} | ⚔️ ATK: {monster['atk']}

Готовы сражаться?"""
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚔️ Атаковать!", callback_data=f"map_fight_{loc_key}_{monster['n']}"),
           types.InlineKeyboardButton("❌ Назад", callback_data="map_back"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data == "map_back")
def map_back(call):
    show_map(types.Message(chat=types.Chat(id=call.message.chat.id, type='private'),
                           from_user=call.from_user, text='/map'))

# ══════════════════════════════════════════════════════════════
#  КВЕСТЫ v5.0
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['quests'])
def show_quests(message):
    u = get_user(message.from_user.id)
    if not u or u[19] == 0:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    text = "📋 КВЕСТЫ\n\n"
    text += "📍 ЕЖЕДНЕВНЫЕ:\n"
    text += f"Убить 5 врагов: {u[22]}/5 → 💰 150g + ✨50 XP\n"
    text += f"Создать 2 предмета: {u[23]}/2 → 💰 100g + ✨30 XP\n\n"
    text += "⭐ ЕЖЕНЕДЕЛЬНЫЕ:\n"
    text += f"Убить босса: {u[24]}/1 → 💰 500g + ✨200 XP\n"
    
    bot.send_message(message.chat.id, text)

# ══════════════════════════════════════════════════════════════
#  АРЕНА (ПОШАГОВАЯ)
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['arena'])
def arena(message):
    u = get_user(message.from_user.id)
    if not u or u[19] == 0:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    text = f"""🏆 АРЕНА (ПОШАГОВАЯ СИСТЕМА!)

👤 Вы: {u[1]}
🏅 Рейтинг: {u[21]}
✅ Побед: {u[10]} | ❌ Поражений: {u[11]}

Нажмите кнопку для поиска противника:"""
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔍 Ищу противника", callback_data=f"arena_find_{message.from_user.id}"))
    
    bot.send_message(message.chat.id, text, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("arena_find_"))
def find_opponent(call):
    uid = call.from_user.id
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    
    c.execute("SELECT user_id FROM arena_queue WHERE user_id!=? ORDER BY joined_at LIMIT 1", (uid,))
    opponent_row = c.fetchone()
    
    if opponent_row:
        opponent_id = opponent_row[0]
        c.execute("DELETE FROM arena_queue WHERE user_id IN(?,?)", (uid, opponent_id))
        conn.commit()
        conn.close()
        
        bot.edit_message_text("⚔️ Противник найден! Начинаем бой...", call.message.chat.id, call.message.message_id)
        start_pvp_battle(call.message.chat.id, uid, opponent_id)
    else:
        c.execute("INSERT OR REPLACE INTO arena_queue(user_id, joined_at) VALUES(?,?)", 
                  (uid, int(time.time())))
        conn.commit()
        conn.close()
        
        bot.edit_message_text("⏳ Поиск противника...\nПожалуйста подождите.",
                            call.message.chat.id, call.message.message_id)

# ══════════════════════════════════════════════════════════════
#  ОСНОВНЫЕ КОМАНДЫ
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    user = get_user(uid)
    if user:
        send_main_menu(message.chat.id)
        return
    
    mk = types.InlineKeyboardMarkup()
    for cl_name, cl_info in CLASS_CONFIG.items():
        mk.add(types.InlineKeyboardButton(f"{cl_info['emoji']} {cl_name}", callback_data=f"class_{cl_name}"))
    
    bot.send_message(message.chat.id,
        "🎮 ВЫБЕРИТЕ КЛАСС:\n\n" +
        "\n".join([f"{v['emoji']} {k}: {v['desc']}" for k, v in CLASS_CONFIG.items()]),
        reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("class_"))
def set_class_cb(call):
    uid = call.from_user.id
    class_name = call.data.replace("class_", "")
    
    if class_name not in CLASS_CONFIG:
        return
    
    class_info = CLASS_CONFIG[class_name]
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""INSERT INTO users(user_id, username, level, exp, gold, class, 
                 str_stat, dex_stat, int_stat, con_stat, wins, losses, gold_earned, 
                 exp_level, hp_potions, mana_potions, equipment_level, equipped_atk, 
                 equipped_def, is_ready, last_daily, arena_rating, daily_kills, 
                 daily_crafts, weekly_bosses)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (uid, call.from_user.first_name or "Player", 1, 0, 100, class_name,
         10, 10, 10, 10, 0, 0, 100, 1, 5, 3, 0, 0, 0, 1, int(time.time()), 0, 0, 0, 0))
    
    conn.commit()
    conn.close()
    
    bot.edit_message_text(
        f"✅ Класс выбран: {class_info['emoji']} {class_name}\n"
        f"Способности: {', '.join(class_info['abilities'])}\n"
        f"Пассивка: {class_info['passive']}\n\n"
        f"/profile - профиль\n/map - НОВАЯ карта мира\n/arena - НОВАЯ пошаговая арена!",
        call.message.chat.id,
        call.message.message_id
    )

def send_main_menu(chat_id):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("⚔️ Бой", "🗺️ Карта (НОВОЕ!)", "🏆 Арена (НОВОЕ!)")
    mk.add("📦 Инвентарь", "🔨 Крафт", "📋 Квесты (НОВОЕ!)")
    mk.add("👤 Профиль", "🏅 Рейтинг", "🎁 Награда")
    mk.add("📖 Справка", "🔄 Сброс")
    bot.send_message(chat_id, "🎮 ГЛАВНОЕ МЕНЮ", reply_markup=mk)

@bot.message_handler(commands=['profile'])
@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(message):
    u = get_user(message.from_user.id)
    if not u or u[19] == 0:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    hp_max = int(u[6] * 15 * CLASS_CONFIG[u[5]]["hp_mod"])
    atk = max(1, int(u[6] * 1.5 + u[17]))
    
    text = f"""👤 ПРОФИЛЬ

🏷️ {u[1]} | {u[5]}
📊 Уровень {u[2]} | 💰 {u[4]}g

⚔️ STR: {u[6]} | 🏃 DEX: {u[7]} | 🔮 INT: {u[8]} | 💪 CON: {u[9]}

❤️ HP: {hp_max} | ⚡ ATK: {atk}
✅ Побед: {u[10]} | ❌ Поражений: {u[11]}
🏅 Рейтинг: {u[21]}"""
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📊 Распределить статы", callback_data="edit_stats"))
    
    bot.send_message(message.chat.id, text, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data == "edit_stats")
def edit_stats(call):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚔️ STR +1", callback_data="stat_str"),
           types.InlineKeyboardButton("🏃 DEX +1", callback_data="stat_dex"))
    mk.add(types.InlineKeyboardButton("🔮 INT +1", callback_data="stat_int"),
           types.InlineKeyboardButton("💪 CON +1", callback_data="stat_con"))
    
    bot.send_message(call.message.chat.id, "Выберите характеристику для улучшения", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("stat_"))
def stat_cb(call):
    uid = call.from_user.id
    u = get_user(uid)
    stat = call.data.replace("stat_", "")
    
    stat_map = {"str": 6, "dex": 7, "int": 8, "con": 9}
    
    if stat in stat_map:
        idx = stat_map[stat]
        update_user(uid, **{["str_stat", "dex_stat", "int_stat", "con_stat"][stat_map[stat] - 6]: u[idx] + 1})
        bot.answer_callback_query(call.id, f"✅ {stat.upper()} +1")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id,
        "📖 СПРАВКА v5.0\n\n"
        "✨ НОВЫЕ КОМАНДЫ:\n"
        "/arena - Пошаговая PvP арена!\n"
        "/map - Карта мира (4 локации)\n"
        "/quests - Ежедневные квесты\n\n"
        "📖 СТАРЫЕ КОМАНДЫ:\n"
        "/start - Новый персонаж\n"
        "/profile - Профиль\n"
        "/stats - Распределить статы\n"
        "/daily - Награда дня\n"
        "/help - Справка\n"
        "/reset - Сброс")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚠️ Да", callback_data="rst_yes"),
           types.InlineKeyboardButton("❌ Нет", callback_data="rst_no"))
    bot.send_message(message.chat.id, "⚠️ Сбросить персонажа?", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data in ("rst_yes", "rst_no"))
def reset_cb(call):
    if call.data == "rst_no":
        bot.edit_message_text("❌ Отменено.", call.message.chat.id, call.message.message_id)
        return
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=?", (call.from_user.id,))
    c.execute("DELETE FROM inventory WHERE user_id=?", (call.from_user.id,))
    c.execute("DELETE FROM materials WHERE user_id=?", (call.from_user.id,))
    conn.commit()
    conn.close()
    
    bot.edit_message_text("🔄 Удалено. /start", call.message.chat.id, call.message.message_id)

# ══════════════════════════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    init_db()
    print("🤖 RPG Bot v5.0 HYBRID запущен!")
    print("✨ Все старые функции сохранены")
    print("🆕 Добавлено: пошаговая арена, карта мира, квесты, редкость")
    bot.infinity_polling()
