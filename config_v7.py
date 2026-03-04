# RPG Bot v7.0 - КОНФИГУРАЦИЯ (враги, локации, рецепты)

CLASSES = {
    "🛡️ Тяжеловес": {"hp_mod": 1.8, "atk_mod": 0.95, "desc": "Макс HP | Защита", "passive": "HP<30%: DEF x1.5"},
    "⚔️ Стеклянная пушка": {"hp_mod": 0.55, "atk_mod": 2.1, "desc": "Макс урон | Крит", "passive": "Крит x3"},
    "👤 Ассасин": {"hp_mod": 0.85, "atk_mod": 1.45, "desc": "Уклон | Скорость", "passive": "+30% урон"},
    "🔮 Мистик": {"hp_mod": 1.05, "atk_mod": 1.15, "desc": "Магия | Баланс", "passive": "INT +5%"},
    "✨ Паладин": {"hp_mod": 1.35, "atk_mod": 1.05, "desc": "Исцеление | Защита", "passive": "20% исцел"},
}

LOCATIONS = {
    "forest": {"name": "🌲 Лес", "desc": "Уровень 1-3 | Волки, пауки | ЛЕГКО", "level": (1, 3)},
    "swamp": {"name": "🏜️ Болото", "desc": "Уровень 4-6 | Зомби, ведьмы | СРЕДНЕ", "level": (4, 6)},
    "mountains": {"name": "⛰️ Горы", "desc": "Уровень 7-10 | Огры, драконы | СЛОЖНО", "level": (7, 10)},
    "castle": {"name": "🏰 Замок", "desc": "Уровень 11-14 | Архимаги, демоны | ЭКСТРА", "level": (11, 14)},
    "dark_cave": {"name": "🕳️ Пещера", "desc": "Уровень 15-18 | Тени, привидения | УЖАС", "level": (15, 18)},
    "abyss": {"name": "⚫ Бездна", "desc": "Уровень 19+ | Боги зла | АД", "level": (19, 999)},
}

MONSTERS = {
    "wolf": {"name": "🐺 Волк", "lvl": 1, "hp": 20, "atk": 8, "xp": 15, "g": 10, "loc": "forest"},
    "spider": {"name": "🕷️ Паук", "lvl": 2, "hp": 15, "atk": 10, "xp": 20, "g": 12, "loc": "forest"},
    "bandit": {"name": "🗡️ Бандит", "lvl": 3, "hp": 25, "atk": 12, "xp": 25, "g": 20, "loc": "forest"},
    "zombie": {"name": "🧟 Зомби", "lvl": 4, "hp": 40, "atk": 14, "xp": 35, "g": 25, "loc": "swamp"},
    "slime": {"name": "💧 Слизень", "lvl": 5, "hp": 30, "atk": 10, "xp": 30, "g": 20, "loc": "swamp"},
    "witch": {"name": "🧙 Ведьма", "lvl": 6, "hp": 45, "atk": 18, "xp": 45, "g": 35, "loc": "swamp"},
    "ogre": {"name": "👹 Огр", "lvl": 8, "hp": 60, "atk": 25, "xp": 60, "g": 50, "loc": "mountains"},
    "drake": {"name": "🐉 Дракончик", "lvl": 10, "hp": 80, "atk": 32, "xp": 85, "g": 75, "loc": "mountains"},
    "knight": {"name": "⚔️ Рыцарь", "lvl": 12, "hp": 100, "atk": 40, "xp": 110, "g": 90, "loc": "castle"},
    "demon": {"name": "👿 Демон", "lvl": 14, "hp": 140, "atk": 55, "xp": 160, "g": 140, "loc": "castle"},
    "shadow": {"name": "👻 Тень", "lvl": 16, "hp": 180, "atk": 65, "xp": 200, "g": 180, "loc": "dark_cave"},
    "abyssal": {"name": "😈 Абиссал", "lvl": 20, "hp": 300, "atk": 100, "xp": 350, "g": 300, "loc": "abyss"},
}

RECIPES = {
    "potion_small": {"name": "🧪 Зелье HP", "mat": {"iron_ore": 1}, "gold": 20, "level": 1},
    "potion_big": {"name": "🧪 Большое зелье", "mat": {"iron_ore": 2}, "gold": 50, "level": 5},
    "sword_iron": {"name": "⚔️ Железный меч", "mat": {"iron_ore": 5}, "gold": 150, "level": 5, "bonus_atk": 5},
    "sword_steel": {"name": "⚔️ Стальной меч", "mat": {"iron_ore": 10}, "gold": 300, "level": 10, "bonus_atk": 12},
    "armor_leather": {"name": "🧥 Кожаная броня", "mat": {"leather": 5}, "gold": 200, "level": 8, "bonus_def": 8},
    "armor_mithril": {"name": "🛡️ Мифриловая", "mat": {"iron_ore": 15, "mana": 3}, "gold": 500, "level": 15, "bonus_def": 20},
    "sword_dragon": {"name": "🐉 Меч дракона", "mat": {"dragon_scale": 3, "mana": 5}, "gold": 1000, "level": 20, "bonus_atk": 30},
}

ACHIEVEMENTS = {
    "first_kill": {"name": "🩸 Первая кровь", "desc": "Убить 1 врага", "reward": 50},
    "level_10": {"name": "⭐ Уровень 10", "desc": "Достичь 10 уровня", "reward": 250},
    "kill_100": {"name": "⚔️ Убийца 100", "desc": "Убить 100 врагов", "reward": 500},
    "arena_10": {"name": "🏆 Чемпион", "desc": "Выиграть 10 в арене", "reward": 400},
}

QUESTS = {
    "daily_kill": {"name": "Убить 5 врагов", "goal": 5, "reward_g": 150, "reward_xp": 50},
    "daily_craft": {"name": "Создать 2 предмета", "goal": 2, "reward_g": 100, "reward_xp": 30},
    "weekly_boss": {"name": "Убить босса", "goal": 1, "reward_g": 500, "reward_xp": 200},
}

RARITY = {
    "common": {"name": "⚪ Обычный", "drop": 50},
    "uncommon": {"name": "🟢 Необычный", "drop": 25},
    "rare": {"name": "🔵 Редкий", "drop": 15},
    "epic": {"name": "🟣 Эпический", "drop": 8},
    "legendary": {"name": "🟡 Легендарный", "drop": 2},
}
