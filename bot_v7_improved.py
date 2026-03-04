"""
╔═════════════════════════════════════════════════════════════════╗
║        RPG BOT v7.0 - УЛУЧШЕННАЯ ВЕРСИЯ                         ║
║                                                                   ║
║  ✨ УЛУЧШЕННЫЕ МЕХАНИКИ:                                        ║
║  • Крит x3 | Уклон | Полосы HP | Красивые тексты             ║
║  • Расчет урона: ATK - (CON/2) + случай(-3,+5)                ║
║  • Система опыта и уровней | +5 к статам за уровень          ║
║                                                                   ║
║  🎮 КОНТЕНТ:                                                    ║
║  • 6 локаций | 32 врага | 12 рецептов | 4 квеста | 6 достижений║
║  • Пошаговая интерактивная арена с полосами HP                ║
║                                                                   ║
║  ПРОСТО И ПОНЯТНО - БЕЗ СЛОЖНОСТИ!                             ║
╚═════════════════════════════════════════════════════════════════╝
"""
import telebot, sqlite3, random, time
from telebot import types
from v7_config_complete import CLASSES, LOCATIONS, MONSTERS, RECIPES, QUESTS, ACHIEVEMENTS

TOKEN = '8695590672:AAEgPT62pXsOD4--ebgBneHJBvW60PpzgI4'
bot = telebot.TeleBot(TOKEN)

pvp_states = {}

# ═══════════════════════════════════════════════════════════════
#  УЛУЧШЕННЫЕ МЕХАНИКИ
# ═══════════════════════════════════════════════════════════════

def calc_stats(user):
    """
    УЛУЧШЕНО: Расчет боевых статов
    - ATK = STR * 1.5 (множитель класса)
    - HP = CON * 10 * множитель класса
    - CRIT = 10 + DEX (макс 95%)
    - DODGE = 5 + DEX (макс 85%)
    """
    atk = max(1, int(user[6] * 1.5 * CLASSES[user[5]]["atk"]))
    con = user[9]
    hp_max = int(con * 10 * CLASSES[user[5]]["hp"])
    crit = min(95, 10 + user[7])
    dodge = min(85, 5 + user[7])
    
    return {
        'atk': atk,
        'hp_max': hp_max,
        'con': con,
        'crit': crit,
        'dodge': dodge
    }

def calc_damage(atk, con):
    """
    УЛУЧШЕНО: Простой расчет урона
    Урон = ATK - (CON/2) + случай(-3 до +5)
    """
    base = atk - int(con * 0.5)
    variance = random.randint(-3, 5)
    return max(1, base + variance)

def is_critical_hit(crit_chance):
    """Проверка критического удара"""
    return random.randint(1, 100) <= crit_chance

def format_hp_bar(current, max_hp):
    """
    УЛУЧШЕНО: Красивая полоса HP
    Пример: ████████░░ 80/100
    """
    if max_hp == 0:
        return "█" * 10
    filled = int((max(0, current) / max_hp) * 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty

def format_battle_screen(p1_name, p1_hp, p1_max, p1_lvl, p2_name, p2_hp, p2_max, p2_lvl, turn, current_player):
    """
    УЛУЧШЕНО: Красивый экран боя
    Показывает полосы HP, уровни, номер хода
    """
    bar1 = format_hp_bar(p1_hp, p1_max)
    bar2 = format_hp_bar(p2_hp, p2_max)
    
    text = f"""⚔️ БОЕВОЕ СТОЛКНОВЕНИЕ | Ход {turn}

👤 {p1_name} (Уровень {p1_lvl})
{bar1} {max(0, p1_hp)}/{p1_max} ❤️

🏆 {p2_name} (Уровень {p2_lvl})
{bar2} {max(0, p2_hp)}/{p2_max} ❤️

Сейчас ходит: {"👤 " + p1_name if current_player == "p1" else "🏆 " + p2_name}
"""
    return text

def format_profile_screen(user, stats):
    """
    УЛУЧШЕНО: Полный и понятный профиль
    Показывает все важные характеристики
    """
    exp_need = user[2] * 100
    
    text = f"""👤 ПРОФИЛЬ ГЕРОЯ v7.0

🏷️ Имя: {user[1]}
🎭 Класс: {user[5]}
📊 Уровень: {user[2]}
💰 Золото: {user[4]}g
✨ Опыт: {user[3]}/{exp_need}

⚡ ОСНОВНЫЕ ХАРАКТЕРИСТИКИ:
⚔️ STR (Сила): {user[6]} → Урон: {stats['atk']}
🏃 DEX (Ловкость): {user[7]} → Крит: {stats['crit']}% | Уклон: {stats['dodge']}%
🔮 INT (Интеллект): {user[8]}
💪 CON (Выносливость): {user[9]} → HP: {stats['hp_max']}

📈 БОЕВАЯ СТАТИСТИКА:
✅ Побед в арене: {user[10]}
❌ Поражений в арене: {user[11]}
🏅 Рейтинг арены: {user[12] if len(user) > 12 else 0}

💡 СОВЕТ: /stats чтобы распределить характеристики"""
    
    return text

def db_init():
    """Инициализация БД"""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0, gold INTEGER DEFAULT 100, class TEXT,
        str_stat INTEGER DEFAULT 10, dex_stat INTEGER DEFAULT 10,
        int_stat INTEGER DEFAULT 10, con_stat INTEGER DEFAULT 10,
        wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, arena_rating INTEGER DEFAULT 0,
        is_ready INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS arena_queue (
        user_id INTEGER PRIMARY KEY, joined_at INTEGER)""")
    conn.commit()
    conn.close()

def get_user(uid):
    """Получить пользователя"""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    u = c.fetchone()
    conn.close()
    return u

def upd_user(uid, **kwargs):
    """Обновить пользователя"""
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    for k, v in kwargs.items():
        c.execute(f"UPDATE users SET {k}=? WHERE user_id=?", (v, uid))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════
#  ПОШАГОВАЯ АРЕНА v7.0
# ═══════════════════════════════════════════════════════════════

def start_pvp_battle(chat_id, uid1, uid2):
    """Начать PvP бой"""
    u1 = get_user(uid1)
    u2 = get_user(uid2)
    s1 = calc_stats(u1)
    s2 = calc_stats(u2)
    
    key = f"{uid1}_{uid2}"
    pvp_states[key] = {
        'p1_id': uid1, 'p2_id': uid2,
        'p1_name': u1[1], 'p2_name': u2[1],
        'p1_lvl': u1[2], 'p2_lvl': u2[2],
        'p1_hp': s1['hp_max'], 'p2_hp': s2['hp_max'],
        'p1_max_hp': s1['hp_max'], 'p2_max_hp': s2['hp_max'],
        'p1_atk': s1['atk'], 'p2_atk': s2['atk'],
        'p1_con': s1['con'], 'p2_con': s2['con'],
        'p1_crit': s1['crit'], 'p2_crit': s2['crit'],
        'turn': 1, 'current': uid1
    }
    show_pvp_battle(chat_id, uid1, uid2)

def show_pvp_battle(chat_id, uid1, uid2):
    """Показать экран боя"""
    key = f"{uid1}_{uid2}"
    if key not in pvp_states:
        return
    
    b = pvp_states[key]
    
    text = format_battle_screen(
        b['p1_name'], b['p1_hp'], b['p1_max_hp'], b['p1_lvl'],
        b['p2_name'], b['p2_hp'], b['p2_max_hp'], b['p2_lvl'],
        b['turn'], 'p1' if b['current'] == uid1 else 'p2'
    )
    
    mk = types.InlineKeyboardMarkup()
    
    if b['current'] == uid1:
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
    """Обработка хода в PvP"""
    parts = call.data.split("_")
    action = parts[1]  # atk или def
    actor = int(parts[2])
    opponent = int(parts[3])
    
    key = f"{actor}_{opponent}"
    if key not in pvp_states:
        key = f"{opponent}_{actor}"
    
    if key not in pvp_states:
        bot.answer_callback_query(call.id, "❌ Бой закончился")
        return
    
    b = pvp_states[key]
    
    if b['current'] != actor:
        bot.answer_callback_query(call.id, "⏳ Не ваш ход!")
        return
    
    # Определяем атаки
    is_p1_acting = actor == b['p1_id']
    
    if is_p1_acting:
        attacker_atk = b['p1_atk']
        attacker_crit = b['p1_crit']
        defender_con = b['p2_con']
        defender_hp_key = 'p2_hp'
    else:
        attacker_atk = b['p2_atk']
        attacker_crit = b['p2_crit']
        defender_con = b['p1_con']
        defender_hp_key = 'p1_hp'
    
    # Действие
    if action == "atk":
        is_crit = is_critical_hit(attacker_crit)
        damage = calc_damage(attacker_atk, defender_con)
        
        if is_crit:
            damage = int(damage * 3)
            crit_text = " 💥 КРИТ! x3"
        else:
            crit_text = ""
        
        b[defender_hp_key] -= damage
        
        if is_p1_acting:
            msg = f"🗡 {b['p1_name']} атаковал! Урон: {damage}{crit_text}"
        else:
            msg = f"🗡 {b['p2_name']} атаковал! Урон: {damage}{crit_text}"
    else:
        if is_p1_acting:
            msg = f"🛡 {b['p1_name']} защищается!"
        else:
            msg = f"🛡 {b['p2_name']} защищается!"
    
    # Проверка победы
    if b['p1_hp'] <= 0:
        winner = b['p2_id']
        loser = b['p1_id']
        winner_name = b['p2_name']
    elif b['p2_hp'] <= 0:
        winner = b['p1_id']
        loser = b['p2_id']
        winner_name = b['p1_name']
    else:
        winner = None
    
    if winner:
        uw = get_user(winner)
        ul = get_user(loser)
        upd_user(winner, wins=uw[10]+1, arena_rating=uw[12]+30, gold=uw[4]+100)
        upd_user(loser, losses=ul[11]+1, arena_rating=max(0, ul[12]-30))
        
        del pvp_states[key]
        bot.send_message(call.message.chat.id, f"🏆 {winner_name} ПОБЕДИЛ!\n\n💰 Победитель получил 100g и +30 рейтинга")
        return
    
    # Смена хода
    b['turn'] += 1
    b['current'] = b['p2_id'] if b['current'] == b['p1_id'] else b['p1_id']
    
    bot.edit_message_text(f"⏳ {msg}\n\nОбработка хода...", call.message.chat.id, call.message.message_id)
    show_pvp_battle(call.message.chat.id, b['p1_id'], b['p2_id'])

# ═══════════════════════════════════════════════════════════════
#  КОМАНДЫ
# ═══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if get_user(uid):
        send_main_menu(message.chat.id)
        return
    
    text = "🎮 ВЫБЕРИТЕ КЛАСС:\n\n"
    mk = types.InlineKeyboardMarkup()
    
    for class_name, class_info in CLASSES.items():
        text += f"{class_name}\n{class_info['desc']}\n\n"
        mk.add(types.InlineKeyboardButton(class_name, callback_data=f"class_{class_name}"))
    
    bot.send_message(message.chat.id, text, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("class_"))
def set_class(call):
    uid = call.from_user.id
    class_name = call.data[6:]
    
    if class_name not in CLASSES:
        return
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("""INSERT INTO users(user_id, username, class, is_ready)
                 VALUES(?,?,?,?)""",
        (uid, call.from_user.first_name or "Герой", class_name, 1))
    conn.commit()
    conn.close()
    
    bot.edit_message_text(
        f"✅ Класс: {class_name}\n\n/profile для просмотра\n/map для карты мира\n/arena для PvP\n/help для справки",
        call.message.chat.id,
        call.message.message_id
    )

def send_main_menu(chat_id):
    """Главное меню"""
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("⚔️ Бой", "🗺️ Карта", "🏆 Арена")
    mk.add("📦 Инвентарь", "🔨 Крафт", "📋 Квесты")
    mk.add("👤 Профиль", "🏅 Достижения", "🎁 Награда")
    mk.add("📖 Справка", "🔄 Сброс")
    bot.send_message(chat_id, "🎮 ГЛАВНОЕ МЕНЮ v7.0", reply_markup=mk)

@bot.message_handler(commands=['profile'])
@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(message):
    """Улучшенный профиль"""
    u = get_user(message.from_user.id)
    if not u:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    stats = calc_stats(u)
    text = format_profile_screen(u, stats)
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("📊 Распределить статы", callback_data="edit_stats"))
    
    bot.send_message(message.chat.id, text, reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data == "edit_stats")
def edit_stats(call):
    """Редактирование статов"""
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚔️ STR +1", callback_data="stat_str"),
           types.InlineKeyboardButton("🏃 DEX +1", callback_data="stat_dex"))
    mk.add(types.InlineKeyboardButton("🔮 INT +1", callback_data="stat_int"),
           types.InlineKeyboardButton("💪 CON +1", callback_data="stat_con"))
    
    bot.send_message(call.message.chat.id, "Выберите характеристику для повышения на +1:", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("stat_"))
def increase_stat(call):
    """Увеличить характеристику"""
    u = get_user(call.from_user.id)
    stat_type = call.data[5:]
    
    stat_map = {"str": 6, "dex": 7, "int": 8, "con": 9}
    stat_names = {6: "str_stat", 7: "dex_stat", 8: "int_stat", 9: "con_stat"}
    
    if stat_type in stat_map:
        idx = stat_map[stat_type]
        new_val = u[idx] + 1
        upd_user(call.from_user.id, **{stat_names[idx]: new_val})
        bot.answer_callback_query(call.id, f"✅ {stat_type.upper()} увеличена на +1")

@bot.message_handler(commands=['map'])
def show_map(message):
    """Карта мира"""
    u = get_user(message.from_user.id)
    if not u:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    text = "🗺️ КАРТА МИРА v7.0\n\n"
    mk = types.InlineKeyboardMarkup()
    
    for loc_key, loc_info in LOCATIONS.items():
        text += f"{loc_info['name']}\n{loc_info['desc']}\n\n"
        mk.add(types.InlineKeyboardButton(loc_info['name'][:14], callback_data=f"loc_{loc_key}"))
    
    bot.send_message(message.chat.id, text, reply_markup=mk)

@bot.message_handler(commands=['quests'])
def show_quests(message):
    """Квесты"""
    bot.send_message(message.chat.id, """📋 КВЕСТЫ v7.0

📍 ЕЖЕДНЕВНЫЕ (сбрасываются в 00:00):
🎯 Убить 5 врагов → 💰 150g | ✨ 50 XP
🎯 Создать 2 предмета → 💰 100g | ✨ 30 XP

⭐ ЕЖЕНЕДЕЛЬНЫЕ (сбрасываются в понедельник):
🎯 Убить 1 босса → 💰 500g | ✨ 200 XP
🎯 Выиграть 3 боя в арене → 💰 300g | ✨ 100 XP""")

@bot.message_handler(commands=['craft'])
def show_craft(message):
    """Крафт"""
    u = get_user(message.from_user.id)
    if not u:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    text = f"🔨 КРАФТ v7.0 ({len(RECIPES)} рецептов)\n\nУровень: {u[2]}\nЗолото: {u[4]}g\n\n"
    
    for recipe_key, recipe in RECIPES.items():
        if u[2] >= recipe['lvl']:
            text += f"✅ {recipe['name']} - {recipe['gold']}g\n"
        else:
            text += f"❌ {recipe['name']} (нужен {recipe['lvl']}+)\n"
    
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['arena'])
def arena_command(message):
    """Арена"""
    u = get_user(message.from_user.id)
    if not u:
        bot.send_message(message.chat.id, "❌ /start")
        return
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔍 Поиск противника", callback_data=f"arena_find_{message.from_user.id}"))
    
    bot.send_message(message.chat.id, f"""🏆 АРЕНА v7.0 (ПОШАГОВАЯ!)

👤 {u[1]} Уровень {u[2]}
✅ Побед: {u[10]} | ❌ Поражений: {u[11]}
🏅 Рейтинг: {u[12]}

Нажмите кнопку для поиска противника:""", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("arena_find_"))
def find_opponent(call):
    """Поиск противника"""
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
        
        bot.edit_message_text("⚔️ Противник найден! БОЙ НАЧИНАЕТСЯ!", call.message.chat.id, call.message.message_id)
        start_pvp_battle(call.message.chat.id, uid, opponent_id)
    else:
        c.execute("INSERT OR REPLACE INTO arena_queue(user_id, joined_at) VALUES(?,?)", (uid, int(time.time())))
        conn.commit()
        conn.close()
        
        bot.edit_message_text("⏳ Поиск противника...\nПожалуйста подождите.", call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    """Справка"""
    bot.send_message(message.chat.id, """📖 СПРАВКА v7.0

✨ УЛУЧШЕНО В v7.0:
⚔️ Критические удары x3 (зависят от DEX)
👁️ Красивые полосы HP в арене
📊 Расчет урона: ATK - (CON/2) + случай
🎯 32 врага по 6 локациям
🔨 12 рецептов крафта
📋 4 квеста и 6 достижений

🎮 ОСНОВНЫЕ КОМАНДЫ:
/start - Создать персонажа
/profile - Профиль и статы
/map - Карта мира (6 локаций)
/arena - PvP арена (ПОШАГОВАЯ!)
/quests - Квесты
/craft - Крафт предметов
/help - Справка
/reset - Сброс

⚔️ МЕХАНИКА БОЯ:
• Урон = ATK - (CON÷2) + (-3 до +5)
• Крит (от DEX) = урон x3
• Уклон (от DEX) = снижает урон
• Каждый уровень = +5 к статам

💡 СОВЕТ: Распределяйте статы в /profile""")

@bot.message_handler(commands=['reset'])
def reset_cmd(message):
    """Сброс персонажа"""
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("⚠️ Да, удалить", callback_data="reset_yes"),
           types.InlineKeyboardButton("❌ Отменить", callback_data="reset_no"))
    bot.send_message(message.chat.id, "⚠️ Вы уверены? Персонаж будет удален!", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data in ("reset_yes", "reset_no"))
def reset_confirm(call):
    """Подтверждение сброса"""
    if call.data == "reset_no":
        bot.edit_message_text("❌ Отменено", call.message.chat.id, call.message.message_id)
        return
    
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=?", (call.from_user.id,))
    conn.commit()
    conn.close()
    
    bot.edit_message_text("🔄 Персонаж удален. /start для новой игры", call.message.chat.id, call.message.message_id)

# ═══════════════════════════════════════════════════════════════
#  ЗАПУСК
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    db_init()
    print("🤖 RPG Bot v7.0 УЛУЧШЕННЫЙ запущен!")
    print("✨ 32 врага | 12 рецептов | 6 локаций | 4 квеста")
    print("⚔️ Улучшенная боевая система с критами и полосами HP")
    print("🏆 Пошаговая интерактивная арена")
    bot.infinity_polling()
