"""
🎮 TERMINAL ADVENTURE GAME
Версия: 2.0
Автор: [Dkosx]
GitHub: https://github.com//terminal-adventure-game

Лицензия: MIT
Copyright (c) 2024 [Ваше Имя]

Исходный код распространяется под лицензией MIT.
Подробнее: https://opensource.org/licenses/MIT
"""

import os
import time
import random
import json
import sys
from enum import Enum
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class GameState(Enum):
    """Состояния игры"""
    MENU = 0
    PLAYING = 1
    WIN = 2
    LOSE = 3
    QUIT = 4
    INVENTORY = 5
    SHOP = 6


class Direction(Enum):
    """Направления движения"""
    NORTH = ("n", "север", "вверх")
    SOUTH = ("s", "юг", "вниз")
    EAST = ("e", "восток", "вправо")
    WEST = ("w", "запад", "влево")

    def __init__(self, command, ru_name, ru_direction):
        self.command = command
        self.ru_name = ru_name
        self.ru_direction = ru_direction


class RoomType(Enum):
    """Типы комнат"""
    EMPTY = ("Пустая комната", "⬜", 60)
    TREASURE = ("Сокровищница", "💰", 15)
    MONSTER = ("Логово монстра", "🐉", 15)
    TRAP = ("Комната с ловушкой", "⚠️ ", 10)
    SHOP = ("Магазин", "🏪", 5)
    EXIT = ("Выход", "🚪", 0)

    def __init__(self, description, icon, weight):
        self.description = description
        self.icon = icon
        self.weight = weight


class Item:
    """Класс предмета"""

    def __init__(self, name: str, description: str, item_type: str, value: int = 0):
        self.name = name
        self.description = description
        self.type = item_type  # weapon, armor, potion, key, treasure
        self.value = value

    def __str__(self):
        return f"{self.name} - {self.description}"


class Player:
    """Класс игрока"""

    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.inventory: List[Item] = []
        self.position = (0, 0)
        self.gold = 100
        self.score = 0
        self.level = 1
        self.experience = 0
        self.kills = 0
        self.weapon: Optional[Item] = None
        self.armor: Optional[Item] = None

    def take_damage(self, damage: int) -> bool:
        """Получение урона с учетом брони"""
        if self.armor:
            damage = max(1, damage - self.armor.value)
        self.health = max(0, self.health - damage)
        return self.health > 0

    def heal(self, amount: int):
        """Лечение"""
        self.health = min(self.max_health, self.health + amount)

    def add_item(self, item: Item):
        """Добавление предмета в инвентарь"""
        self.inventory.append(item)

    def remove_item(self, item: Item) -> bool:
        """Удаление предмета из инвентаря"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def add_experience(self, exp: int):
        """Добавление опыта"""
        self.experience += exp
        while self.experience >= self.level * 100:
            self.level_up()

    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.experience = 0
        self.max_health += 20
        self.health = self.max_health
        print(f"\n🎉 УРОВЕНЬ ПОВЫШЕН! Теперь вы {self.level} уровня!")
        print(f"❤️  Максимальное здоровье увеличено до {self.max_health}")

    def get_attack_damage(self) -> int:
        """Получение урона атаки с учетом оружия"""
        base_damage = random.randint(10, 20)
        if self.weapon:
            return base_damage + self.weapon.value
        return base_damage

    def show_stats(self) -> str:
        """Показать статистику игрока"""
        health_percent = self.health / self.max_health
        health_bar_length = 20
        filled = int(health_percent * health_bar_length)
        health_bar = "█" * filled + "░" * (health_bar_length - filled)

        exp_percent = (self.experience / (self.level * 100)) * 100
        exp_bar_length = 15
        exp_filled = int((exp_percent / 100) * exp_bar_length)
        exp_bar = "▓" * exp_filled + "░" * (exp_bar_length - exp_filled)

        return f"""
{'='*50}
👤 ИГРОК: {self.name} (Уровень {self.level})
{'='*50}
❤️  ЗДОРОВЬЕ: [{health_bar}] {self.health}/{self.max_health}
⭐ ОПЫТ: [{exp_bar}] {self.experience}/{self.level * 100}
💰 ЗОЛОТО: {self.gold} монет
🏆 ОЧКИ: {self.score}
⚔️  УБИТО МОНСТРОВ: {self.kills}
🗺️  ПОЗИЦИЯ: [{self.position[0]}, {self.position[1]}]

⚔️  ОРУЖИЕ: {self.weapon.name if self.weapon else 'Нет'}
🛡️  БРОНЯ: {self.armor.name if self.armor else 'Нет'}

🎒 ИНВЕНТАРЬ ({len(self.inventory)}/20):
{self.show_inventory_items()}
{'='*50}
        """

    def show_inventory_items(self) -> str:
        """Показать предметы в инвентаре"""
        if not self.inventory:
            return "  Пусто"

        items_by_type: Dict[str, List[Item]] = {}
        for item in self.inventory:
            if item.type not in items_by_type:
                items_by_type[item.type] = []
            items_by_type[item.type].append(item)

        result = []
        type_names = {
            'weapon': '⚔️  Оружие',
            'armor': '🛡️  Броня',
            'potion': '🧪 Зелья',
            'treasure': '💰 Сокровища',
            'key': '🗝️  Ключи',
            'other': '📦 Разное'
        }

        for item_type, items in items_by_type.items():
            type_name = type_names.get(item_type, '📦 Разное')
            result.append(f"  {type_name}:")
            for item in items:
                result.append(f"    • {item.name}")

        return "\n".join(result)


class Monster:
    """Класс монстра"""

    def __init__(self, level: int = 1):
        self.level = level
        self.name = self.generate_name()
        self.health = 20 + (level * 10)
        self.max_health = self.health
        self.damage = 5 + level
        self.experience = 10 * level
        self.gold = random.randint(5, 20) * level

    @staticmethod
    def generate_name() -> str:
        """Генерация имени монстра"""
        prefixes = ['Яростный', 'Древний', 'Могучий', 'Жуткий', 'Коварный']
        types = ['Гоблин', 'Орк', 'Тролль', 'Скелет', 'Зомби', 'Паук', 'Волк']
        suffixes = ['Разрушитель', 'Убийца', 'Пожиратель', 'Страж', 'Властитель']

        if random.random() < 0.3:
            return f"{random.choice(prefixes)} {random.choice(types)}"
        elif random.random() < 0.5:
            return f"{random.choice(types)} {random.choice(suffixes)}"
        else:
            return random.choice(types)

    def take_damage(self, damage: int) -> bool:
        """Получение урона монстром"""
        self.health = max(0, self.health - damage)
        return self.health > 0

    def show_health(self) -> str:
        """Показать здоровье монстра"""
        health_percent = self.health / self.max_health
        health_bar_length = 15
        filled = int(health_percent * health_bar_length)
        return f"[{'█' * filled}{'░' * (health_bar_length - filled)}] {self.health}/{self.max_health}"


class Shop:
    """Класс магазина"""

    def __init__(self):
        self.items = [
            Item("Малое зелье здоровья", "Восстанавливает 30 HP", "potion", 30),
            Item("Большое зелье здоровья", "Восстанавливает 60 HP", "potion", 60),
            Item("Стальной меч", "+5 к урону", "weapon", 5),
            Item("Мифриловый меч", "+10 к урону", "weapon", 10),
            Item("Кожаная броня", "+3 к защите", "armor", 3),
            Item("Стальная броня", "+7 к защите", "armor", 7),
            Item("Карта сокровищ", "Показывает ближайшее сокровище", "other", 0),
            Item("Факел", "Помогает избегать ловушек", "other", 0)
        ]
        self.prices = {
            "Малое зелье здоровья": 20,
            "Большое зелье здоровья": 40,
            "Стальной меч": 50,
            "Мифриловый меч": 100,
            "Кожаная броня": 30,
            "Стальная броня": 70,
            "Карта сокровищ": 25,
            "Факел": 15
        }

    def show_items(self, player: Player) -> str:
        """Показать товары в магазине"""
        result = ["\n🏪 МАГАЗИН:", "=" * 40]

        for i, item in enumerate(self.items, 1):
            price = self.prices[item.name]
            affordable = "🟢" if player.gold >= price else "🔴"
            result.append(f"{i}. {affordable} {item.name} - {price} золота")
            result.append(f"   📝 {item.description}")

        result.append("="*40)
        result.append(f"💰 Ваше золото: {player.gold}")
        result.append("="*40)
        return "\n".join(result)


class GameMap:
    """Класс игровой карты"""

    def __init__(self, size: int = 6):
        self.size = size
        self.rooms: Dict[Tuple[int, int], dict] = {}
        self.generate_map()

    def generate_map(self):
        """Генерация случайной карты"""
        # Создаем все комнаты
        room_types = [rt for rt in RoomType if rt != RoomType.EXIT]
        weights = [rt.weight for rt in room_types]

        for x in range(self.size):
            for y in range(self.size):
                room_type = random.choices(room_types, weights=weights)[0]
                self.rooms[(x, y)] = {
                    'type': room_type,
                    'visited': False,
                    'description': self.get_room_description(room_type),
                    'processed': False,
                    'has_treasure': room_type == RoomType.TREASURE,
                    'has_monster': room_type == RoomType.MONSTER,
                    'is_trap_active': room_type == RoomType.TRAP
                }

        # Устанавливаем стартовую позицию
        self.rooms[(0, 0)]['type'] = RoomType.EMPTY
        self.rooms[(0, 0)]['visited'] = True
        self.rooms[(0, 0)]['processed'] = True

        # Устанавливаем выход
        exit_pos = (self.size-1, self.size-1)
        self.rooms[exit_pos]['type'] = RoomType.EXIT
        self.rooms[exit_pos]['description'] = "🚪 Выход из подземелья!"

    @staticmethod
    def get_room_description(room_type: RoomType) -> str:
        """Получить описание комнаты"""
        descriptions = {
            RoomType.EMPTY: [
                "Пустая каменная комната. Слышно капание воды.",
                "Заброшенное помещение. Пахнет плесенью.",
                "Небольшая комнатка с разбитой посудой.",
                "Зал с колоннами. Эхо разносит каждый звук."
            ],
            RoomType.TREASURE: [
                "Комната сверкает золотом! Здесь явно есть сокровища!",
                "Сундук стоит посреди комнаты. Он выглядит старым, но целым.",
                "На столе разбросаны драгоценные камни и монеты."
            ],
            RoomType.MONSTER: [
                "Из темноты слышно рычание... Здесь кто-то есть!",
                "На стенах видны свежие царапины. Будьте осторожны!",
                "Воздух наполнен зловонием. Что-то большое здесь обитает."
            ],
            RoomType.TRAP: [
                "Пол выглядит подозрительно... Возможно, здесь ловушки.",
                "На стенах видны отверстия для стрел. Опасно!",
                "Деревянные доски на полу выглядят ненадежно."
            ],
            RoomType.SHOP: [
                "Небольшая лавка со множеством товаров.",
                "Старик за прилавком смотрит на вас с интересом.",
                "Полки ломятся от различных предметов и зелий."
            ],
            RoomType.EXIT: [
                "🚪 Выход из подземелья!",
                "Свет проникает в комнату. Это выход!",
                "Дверь с золотой ручкой ведет на свободу!"
            ]
        }
        return random.choice(descriptions.get(room_type, ["Неизвестная комната."]))

    def get_current_room_info(self, position: Tuple[int, int]) -> Optional[dict]:
        """Получить информацию о текущей комнате"""
        return self.rooms.get(position, None)

    def mark_visited(self, position: Tuple[int, int]):
        """Пометить комнату как посещенную"""
        if position in self.rooms:
            self.rooms[position]['visited'] = True

    def draw_minimap(self, player_pos: Tuple[int, int]):
        """Нарисовать миникарту"""
        print("\n" + "="*50)
        print("🗺️  КАРТА ПОДЗЕМЕЛЬЯ:")
        print("="*50)

        for y in range(self.size):
            row = []
            for x in range(self.size):
                pos = (x, y)
                room = self.rooms[pos]

                if pos == player_pos:
                    row.append("👤")  # Игрок
                elif room['type'] == RoomType.EXIT:
                    row.append("🚪")  # Выход
                elif room['type'] == RoomType.TREASURE:
                    row.append("💰")  # Сокровище
                elif room['type'] == RoomType.MONSTER:
                    row.append("🐉")  # Монстр
                elif room['type'] == RoomType.TRAP:
                    row.append("⚠️ ")  # Ловушка
                elif room['type'] == RoomType.SHOP:
                    row.append("🏪")  # Магазин
                elif room['visited']:
                    row.append("⬜")  # Посещенная
                else:
                    row.append("⬛")  # Неизвестная
            print("  ".join(row))

        print("\n" + "="*50)
        print("ЛЕГЕНДА:")
        print("👤 - Вы, ⬜ - посещено, ⬛ - неизвестно")
        print("💰 - сокровище, 🐉 - монстр, ⚠️  - ловушка")
        print("🏪 - магазин, 🚪 - выход")
        print("="*50)


class Game:
    """Основной класс игры"""

    def __init__(self):
        self.state = GameState.MENU
        self.map = GameMap()
        self.player: Optional[Player] = None
        self.shop = Shop()
        self.game_time = 0
        self.start_time = time.time()
        self.save_file = "savegame.json"

    @staticmethod
    def clear_screen():
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def show_title():
        """Показать заголовок игры"""
        title = r"""
╔══════════════════════════════════════════════════╗
║        🎮 ТЕРМИНАЛЬНОЕ ПРИКЛЮЧЕНИЕ v2.0         ║
║           ПОДЗЕМЕЛЬЕ ДРЕВНИХ ТАЙН               ║
╚══════════════════════════════════════════════════╝
        """
        print(title)

    @staticmethod
    def show_help():
        """Показать справку"""
        help_text = """
╔══════════════════════════════════════════════════╗
║                  🎮 СПРАВКА                      ║
╚══════════════════════════════════════════════════╝

ДВИЖЕНИЕ:
  N / С - Север (вверх)
  S / Ю - Юг (вниз)
  E / В - Восток (вправо)
  W / З - Запад (влево)

ОСНОВНЫЕ КОМАНДЫ:
  M - Показать карту
  I - Инвентарь и статистика
  H - Эта справка
  S - Сохранить игру
  L - Загрузить игру
  Q - Выйти в меню

В БОЮ:
  1 - Атаковать
  2 - Защититься (уменьшает урон на 50%)
  3 - Использовать зелье
  4 - Попытаться убежать (60% шанс)

В МАГАЗИНЕ:
  1-8 - Купить предмет
  Q - Выйти из магазина

ЦЕЛЬ ИГРЫ:
  Найти выход (🚪) в правом нижнем углу карты
  Собрать как можно больше сокровищ
  Повышать уровень и улучшать снаряжение
  Остаться в живых!

╔══════════════════════════════════════════════════╗
║            УДАЧИ В ПРИКЛЮЧЕНИИ!                  ║
╚══════════════════════════════════════════════════╝
        """
        print(help_text)
        input("\nНажмите Enter чтобы продолжить...")

    def show_menu(self):
        """Показать главное меню"""
        while self.state == GameState.MENU:
            self.clear_screen()
            self.show_title()

            print("\n" + "="*50)
            print("            ГЛАВНОЕ МЕНУ")
            print("="*50)
            print("1. 🎮 Новая игра")
            print("2. ⏮️  Продолжить игру")
            print("3. 🏆 Таблица рекордов")
            print("4. 🎮 Как играть")
            print("5. 🚪 Выход")
            print("="*50)

            choice = input("\nВыберите действие (1-5): ").strip()

            if choice == "1":
                self.setup_player()
                self.state = GameState.PLAYING
            elif choice == "2":
                if self.load_game():
                    print("✅ Игра загружена!")
                    input("\nНажмите Enter чтобы продолжить...")
                    self.state = GameState.PLAYING
                else:
                    print("❌ Файл сохранения не найден!")
                    input("\nНажмите Enter чтобы вернуться в меню...")
            elif choice == "3":
                self.show_highscores()
            elif choice == "4":
                self.show_help()
            elif choice == "5":
                print("\nДо свидания! Спасибо за игру! 🎮")
                sys.exit(0)
            else:
                print("❌ Неверный выбор!")
                time.sleep(1)

    def setup_player(self):
        """Настройка игрока"""
        self.clear_screen()
        self.show_title()

        print("\n" + "="*50)
        print("         СОЗДАНИЕ ПЕРСОНАЖА")
        print("="*50)

        name = input("\nВведите имя вашего героя: ").strip()
        if not name:
            name = "Безымянный Герой"

        self.player = Player(name)

        # Стартовые предметы
        starter_items = [
            Item("Деревянный меч", "Простое оружие новичка", "weapon", 2),
            Item("Кожаный доспех", "Легкая защита", "armor", 1),
            Item("Малое зелье здоровья", "Восстанавливает 30 HP", "potion", 30),
            Item("Карта подземелья", "Показывает ваше местоположение", "other", 0),
            Item("Факел", "Освещает путь", "other", 0)
        ]

        for item in starter_items:
            self.player.add_item(item)

        # Экипировка стартового оружия и брони
        self.player.weapon = starter_items[0]
        self.player.armor = starter_items[1]

        print(f"\n👤 Добро пожаловать, {self.player.name}!")
        print("🎒 Вы начинаете с базовым снаряжением:")
        print("   ⚔️  Деревянный меч (+2 к урону)")
        print("   🛡️  Кожаный доспех (+1 к защите)")
        print("   🧪 Малое зелье здоровья")
        print("   🗺️  Карта подземелья")
        print("   🔦 Факел")
        print(f"\n💰 Начальный капитал: {self.player.gold} золота")

        input("\nНажмите Enter чтобы начать приключение...")

    def save_game(self) -> bool:
        """Сохранить игру"""
        if not self.player:
            return False

        save_data: Dict[str, Any] = {
            'player': {
                'name': self.player.name,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'position': list(self.player.position),
                'gold': self.player.gold,
                'score': self.player.score,
                'level': self.player.level,
                'experience': self.player.experience,
                'kills': self.player.kills,
                'inventory': [
                    {
                        'name': item.name,
                        'description': item.description,
                        'type': item.type,
                        'value': item.value
                    }
                    for item in self.player.inventory
                ]
            },
            'map': {
                'size': self.map.size,
                'rooms': {}
            },
            'timestamp': datetime.now().isoformat(),
            'playtime': time.time() - self.start_time
        }

        # Добавляем оружие если есть
        if self.player.weapon:
            save_data['player']['weapon'] = {
                'name': self.player.weapon.name,
                'description': self.player.weapon.description,
                'type': self.player.weapon.type,
                'value': self.player.weapon.value
            }

        # Добавляем броню если есть
        if self.player.armor:
            save_data['player']['armor'] = {
                'name': self.player.armor.name,
                'description': self.player.armor.description,
                'type': self.player.armor.type,
                'value': self.player.armor.value
            }

        # Сохраняем информацию о комнатах
        for pos, room in self.map.rooms.items():
            save_data['map']['rooms'][f"{pos[0]},{pos[1]}"] = {
                'type': room['type'].name,
                'visited': room['visited'],
                'processed': room['processed']
            }

        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print("✅ Игра успешно сохранена!")
            return True
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return False

    def load_game(self) -> bool:
        """Загрузить игру"""
        try:
            if not os.path.exists(self.save_file):
                return False

            with open(self.save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Восстанавливаем игрока
            player_data = save_data['player']
            self.player = Player(player_data['name'])
            self.player.health = player_data['health']
            self.player.max_health = player_data['max_health']
            self.player.position = tuple(player_data['position'])
            self.player.gold = player_data['gold']
            self.player.score = player_data['score']
            self.player.level = player_data['level']
            self.player.experience = player_data['experience']
            self.player.kills = player_data['kills']

            # Восстанавливаем инвентарь
            self.player.inventory = []
            for item_data in player_data['inventory']:
                item = Item(
                    item_data['name'],
                    item_data['description'],
                    item_data['type'],
                    item_data['value']
                )
                self.player.add_item(item)

            # Восстанавливаем оружие и броню
            if 'weapon' in player_data and player_data['weapon']:
                weapon_data = player_data['weapon']
                weapon = Item(
                    weapon_data['name'],
                    weapon_data['description'],
                    weapon_data['type'],
                    weapon_data['value']
                )
                self.player.weapon = weapon

            if 'armor' in player_data and player_data['armor']:
                armor_data = player_data['armor']
                armor = Item(
                    armor_data['name'],
                    armor_data['description'],
                    armor_data['type'],
                    armor_data['value']
                )
                self.player.armor = armor

            # Восстанавливаем карту
            map_data = save_data['map']
            self.map = GameMap(map_data['size'])

            for pos_str, room_data in map_data['rooms'].items():
                x, y = map(int, pos_str.split(','))
                pos = (x, y)

                if pos in self.map.rooms:
                    self.map.rooms[pos]['visited'] = room_data['visited']
                    self.map.rooms[pos]['processed'] = room_data['processed']

            self.start_time = time.time() - save_data.get('playtime', 0)
            return True

        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return False

    def show_highscores(self):
        """Показать таблицу рекордов"""
        self.clear_screen()
        print("\n" + "="*50)
        print("            🏆 ТАБЛИЦА РЕКОРДОВ")
        print("="*50)

        highscores = []
        if os.path.exists("highscores.json"):
            try:
                with open("highscores.json", 'r', encoding='utf-8') as f:
                    highscores = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        if not highscores:
            print("\n   Пока здесь пусто...")
            print("   Станьте первым чемпионом!")
        else:
            # Сортируем по очкам
            highscores.sort(key=lambda x: x.get('score', 0), reverse=True)

            print("\n№  Имя                 Очки   Уровень  Время")
            print("-" * 50)

            for i, score in enumerate(highscores[:10], 1):
                name = score.get('name', 'Неизвестный')[:18].ljust(18)
                score_val = str(score.get('score', 0)).rjust(6)
                level = str(score.get('level', 1)).rjust(3)
                playtime = time.strftime("%M:%S", time.gmtime(score.get('playtime', 0)))

                medal = ""
                if i == 1:
                    medal = "🥇 "
                elif i == 2:
                    medal = "🥈 "
                elif i == 3:
                    medal = "🥉 "

                print(f"{i:2}.{medal}{name} {score_val}   {level}     {playtime}")

        print("="*50)
        input("\nНажмите Enter чтобы вернуться...")

    def save_highscore(self):
        """Сохранить рекорд"""
        if not self.player:
            return

        playtime = time.time() - self.start_time

        highscore = {
            'name': self.player.name,
            'score': self.player.score,
            'level': self.player.level,
            'kills': self.player.kills,
            'gold': self.player.gold,
            'playtime': playtime,
            'timestamp': datetime.now().isoformat()
        }

        highscores = []
        if os.path.exists("highscores.json"):
            try:
                with open("highscores.json", 'r', encoding='utf-8') as f:
                    highscores = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        highscores.append(highscore)

        try:
            with open("highscores.json", 'w', encoding='utf-8') as f:
                json.dump(highscores, f, ensure_ascii=False, indent=2)
        except (IOError, OSError):
            pass

    def handle_room_event(self, room_info: dict) -> bool:
        """Обработка событий в комнате"""
        room_type = room_info['type']

        if room_type == RoomType.TREASURE and not room_info['processed']:
            print("\n💰 ВЫ НАШЛИ СОКРОВИЩЕ!")

            treasures = [
                Item("Золотой слиток", "Ценный металл", "treasure", 50),
                Item("Волшебный амулет", "Таинственный артефакт", "treasure", 75),
                Item("Древний свиток", "Записи древних мудрецов", "treasure", 60),
                Item("Самоцвет", "Сверкающий драгоценный камень", "treasure", 40),
                Item("Королевская корона", "Дорогая регалия", "treasure", 100)
            ]

            treasure = random.choice(treasures)
            gold_found = random.randint(20, 100)

            self.player.add_item(treasure)
            self.player.gold += gold_found
            self.player.score += treasure.value

            print(f"📦 Вы получили: {treasure.name} (+{treasure.value} очков)")
            print(f"💰 Нашли {gold_found} золота")
            print(f"💰 Теперь у вас: {self.player.gold} золота")

            room_info['processed'] = True
            room_info['has_treasure'] = False
            input("\nНажмите Enter чтобы продолжить...")
            return True

        elif room_type == RoomType.MONSTER and not room_info['processed']:
            print("\n🐉 НА ВАС НАПАЛ МОНСТР!")

            monster = Monster(self.player.level)
            print(f"Перед вами {monster.name} (Уровень {monster.level})!")
            print(f"❤️  Здоровье монстра: {monster.show_health()}")

            # Бой с монстром
            while monster.health > 0 and self.player.health > 0:
                print("\n" + "="*40)
                print(f"Ваше здоровье: ❤️ {self.player.health}/{self.player.max_health}")
                print(f"Здоровье {monster.name}: {monster.show_health()}")
                print("="*40)

                print("\nВыберите действие:")
                print("1. ⚔️  Атаковать")
                print("2. 🛡️  Защититься (уменьшает урон на 50%)")
                print("3. 🧪 Использовать зелье")
                print("4. 🏃 Попытаться убежать (60% шанс)")

                choice = input("Ваш выбор (1-4): ").strip()

                if choice == "1":
                    # Атака игрока
                    player_damage = self.player.get_attack_damage()
                    monster.take_damage(player_damage)
                    print(f"\n⚔️  Вы нанесли {player_damage} урона!")

                elif choice == "2":
                    # Защита
                    print(f"\n🛡️  Вы подняли щит! Следующая атака будет слабее.")
                    # Флаг защиты будет учтен при получении урона

                elif choice == "3":
                    # Использование зелья
                    potions = [item for item in self.player.inventory if item.type == "potion"]
                    if potions:
                        potion = potions[0]
                        self.player.heal(potion.value)
                        self.player.remove_item(potion)
                        print(f"\n🧪 Вы использовали {potion.name}!")
                        print(f"❤️  Восстановлено {potion.value} здоровья")
                    else:
                        print("\n❌ У вас нет зелий!")
                        continue

                elif choice == "4":
                    # Попытка убежать
                    if random.random() < 0.6:
                        print("\n🏃 Вам удалось сбежать!")
                        input("Нажмите Enter чтобы продолжить...")
                        return False
                    else:
                        print("\n❌ Не удалось сбежать! Монстр атакует!")
                else:
                    print("\n❌ Неверный выбор! Монстр атакует!")

                # Атака монстра (если не убежали)
                if choice != "4" and monster.health > 0:
                    monster_damage = monster.damage

                    # Учет защиты
                    if choice == "2":
                        monster_damage = max(1, monster_damage // 2)
                        print(f"🛡️  Защита уменьшила урон до {monster_damage}")

                    is_alive = self.player.take_damage(monster_damage)
                    print(f"🐉 {monster.name} наносит вам {monster_damage} урона!")

                    if not is_alive:
                        print("\n💀 ВЫ ПОГИБЛИ В БОЮ!")
                        self.state = GameState.LOSE
                        input("Нажмите Enter чтобы продолжить...")
                        return False

            if monster.health <= 0:
                print(f"\n🎉 Вы победили {monster.name}!")
                self.player.add_experience(monster.experience)
                self.player.gold += monster.gold
                self.player.score += monster.experience * 2
                self.player.kills += 1

                print(f"⭐ Получено {monster.experience} опыта")
                print(f"💰 Получено {monster.gold} золота")
                print(f"🏆 +{monster.experience * 2} очков")
                print(f"⚔️  Всего убито: {self.player.kills} монстров")

                room_info['processed'] = True
                room_info['has_monster'] = False
                input("\nНажмите Enter чтобы продолжить...")
                return True

        elif room_type == RoomType.TRAP and not room_info['processed']:
            print("\n⚠️  ВЫ АКТИВИРОВАЛИ ЛОВУШКУ!")
            trap_damage = random.randint(10, 30)

            # Шанс избежать ловушку
            has_torch = any(item.name == "Факел" for item in self.player.inventory)
            if has_torch and random.random() < 0.6:
                print("🔥 Благодаря факелу вы заметили и избежали ловушку!")
            else:
                is_alive = self.player.take_damage(trap_damage)
                print(f"💥 Вы получили {trap_damage} урона от ловушки!")

                if not is_alive:
                    print("\n💀 ВЫ ПОГИБЛИ ОТ ЛОВУШКИ!")
                    self.state = GameState.LOSE
                    input("Нажмите Enter чтобы продолжить...")
                    return False

            room_info['processed'] = True
            room_info['is_trap_active'] = False
            input("Нажмите Enter чтобы продолжить...")
            return True

        elif room_type == RoomType.SHOP:
            print("\n🏪 ДОБРО ПОЖАЛОВАТЬ В МАГАЗИН!")
            print("Здесь вы можете купить полезные предметы.")

            while True:
                self.clear_screen()
                print(self.shop.show_items(self.player))

                print("\nВыберите номер предмета для покупки (1-8)")
                print("или Q чтобы выйти из магазина")

                choice = input("\nВаш выбор: ").lower().strip()

                if choice == 'q':
                    print("\nВозвращаемся к приключениям!")
                    input("Нажмите Enter чтобы продолжить...")
                    break

                try:
                    item_index = int(choice) - 1
                    if 0 <= item_index < len(self.shop.items):
                        item = self.shop.items[item_index]
                        price = self.shop.prices[item.name]

                        if self.player.gold >= price:
                            self.player.gold -= price
                            self.player.add_item(item)
                            print(f"\n✅ Вы купили {item.name} за {price} золота!")
                            print(f"💰 Осталось золота: {self.player.gold}")
                        else:
                            print(f"\n❌ Недостаточно золота! Нужно {price}, а у вас {self.player.gold}")
                    else:
                        print("\n❌ Неверный номер предмета!")
                except ValueError:
                    print("\n❌ Неверный ввод!")

                input("\nНажмите Enter чтобы продолжить...")

            return True

        elif room_type == RoomType.EXIT:
            print("\n🎉 ВЫ НАШЛИ ВЫХОД ИЗ ПОДЗЕМЕЛЬЯ!")
            print("="*40)
            print("🎊 ПОБЕДА! ИГРА ПРОЙДЕНА!")
            print("="*40)
            self.state = GameState.WIN
            input("Нажмите Enter чтобы продолжить...")
            return False

        return True

    def move_player(self, direction):
        """Перемещение игрока"""
        x, y = self.player.position

        if direction == Direction.NORTH and y > 0:
            y -= 1
        elif direction == Direction.SOUTH and y < self.map.size - 1:
            y += 1
        elif direction == Direction.EAST and x < self.map.size - 1:
            x += 1
        elif direction == Direction.WEST and x > 0:
            x -= 1
        else:
            print("❌ Нельзя идти в этом направлении!")
            input("Нажмите Enter чтобы продолжить...")
            return False

        self.player.position = (x, y)
        self.map.mark_visited((x, y))
        return True

    def game_loop(self):
        """Основной игровой цикл"""
        while self.state == GameState.PLAYING:
            self.clear_screen()
            self.show_title()

            # Показать статистику
            print(self.player.show_stats())

            # Показать текущую позицию
            x, y = self.player.position
            print(f"📍 Ваша позиция: [{x}, {y}]")

            # Получить информацию о текущей комнате
            room_info = self.map.get_current_room_info(self.player.position)
            if room_info:
                print(f"\n📝 {room_info['description']}")

                # Если комната еще не посещалась, обработать событие
                if not room_info.get('processed', False):
                    result = self.handle_room_event(room_info)
                    if not result:
                        break

            # Проверка состояния игры
            if self.state != GameState.PLAYING:
                break

            # Проверка здоровья
            if self.player.health <= 0:
                print("\n💀 ВЫ ПОГИБЛИ...")
                self.state = GameState.LOSE
                break

            # Показать доступные направления
            print("\n" + "="*40)
            print("КУДА ИДТИ ДАЛЬШЕ?")
            print("="*40)

            x, y = self.player.position
            directions = []

            if y > 0:
                directions.append("N - Север")
            if y < self.map.size - 1:
                directions.append("S - Юг")
            if x < self.map.size - 1:
                directions.append("E - Восток")
            if x > 0:
                directions.append("W - Запад")

            if directions:
                print("Доступные направления:")
                for direction in directions:
                    print(f"  {direction}")
            else:
                print("Нет доступных направлений!")

            print("\nДругие команды:")
            print("  M - Карта, I - Инвентарь, H - Помощь")
            print("  S - Сохранить, L - Загрузить, Q - Выход в меню")

            # Получение команды от игрока
            command = input("\nВаша команда: ").lower().strip()

            # Обработка команд
            if command in ['n', 'north', 'с', 'север']:
                self.move_player(Direction.NORTH)
            elif command in ['s', 'south', 'ю', 'юг']:
                self.move_player(Direction.SOUTH)
            elif command in ['e', 'east', 'в', 'восток']:
                self.move_player(Direction.EAST)
            elif command in ['w', 'west', 'з', 'запад']:
                self.move_player(Direction.WEST)
            elif command == 'm':
                self.map.draw_minimap(self.player.position)
                input("\nНажмите Enter чтобы продолжить...")
            elif command == 'i':
                print(self.player.show_stats())
                input("\nНажмите Enter чтобы продолжить...")
            elif command == 'h':
                self.show_help()
            elif command == 's':
                self.save_game()
                input("\nНажмите Enter чтобы продолжить...")
            elif command == 'l':
                if self.load_game():
                    print("✅ Игра загружена!")
                else:
                    print("❌ Не удалось загрузить игру!")
                input("\nНажмите Enter чтобы продолжить...")
            elif command == 'q':
                print("\n🚪 Вы уверены что хотите выйти в меню? (y/n)")
                if input().lower() == 'y':
                    self.state = GameState.MENU
                    break
                else:
                    print("Продолжаем игру!")
                    time.sleep(1)
            else:
                print("❌ Неизвестная команда. Введите 'h' для справки.")
                input("Нажмите Enter чтобы продолжить...")

    def show_game_over(self):
        """Показать экран завершения игры"""
        self.clear_screen()
        self.show_title()

        game_time = time.time() - self.start_time
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)

        print("\n" + "="*50)

        if self.state == GameState.WIN:
            print("🎉🎉🎉 ПОЗДРАВЛЯЕМ! 🎉🎉🎉")
            print("Вы успешно выбрались из подземелья!")
        elif self.state == GameState.LOSE:
            print("💀 ИГРА ОКОНЧЕНА")
            print("Ваше приключение завершилось неудачей...")
        else:
            print("🚪 ИГРА ПРЕРВАНА")

        print("="*50)
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"👤 Игрок: {self.player.name}")
        print(f"⏱️  Время игры: {minutes} мин {seconds} сек")
        print(f"⭐ Набрано очков: {self.player.score}")
        print(f"🎒 Собрано предметов: {len(self.player.inventory)}")
        print(f"❤️  Осталось здоровья: {self.player.health}")
        print(f"💰 Золото: {self.player.gold}")
        print(f"⚔️  Убито монстров: {self.player.kills}")
        print(f"📈 Уровень: {self.player.level}")

        # Рейтинг
        if self.player.score >= 500:
            rating = "🌟 ЛЕГЕНДАРНЫЙ ГЕРОЙ 🌟"
        elif self.player.score >= 300:
            rating = "🏆 ВЕЛИКИЙ ИСКАТЕЛЬ"
        elif self.player.score >= 150:
            rating = "⚔️  ОПЫТНЫЙ ВОИН"
        elif self.player.score >= 50:
            rating = "🎯 НАЧИНАЮЩИЙ ГЕРОЙ"
        else:
            rating = "👶 НОВИЧОК"

        print(f"\n🏅 Ваш рейтинг: {rating}")
        print("\n" + "="*50)

        if self.state == GameState.WIN:
            self.save_highscore()
            print("🏆 Ваш рекорд сохранен в таблице лидеров!")

        print("\nХотите сыграть еще раз? (y/n)")
        if input().lower() == 'y':
            return True
        return False

    def run(self):
        """Запуск игры"""
        while True:
            self.show_menu()

            if self.state == GameState.PLAYING:
                self.game_loop()

                if not self.show_game_over():
                    print("\nСпасибо за игру! До новых встреч! 🎮")
                    break

                # Перезапуск игры
                self.__init__()


def main():
    """Точка входа в программу"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем.")
    except Exception as e:
        print(f"\n⚠️  Произошла ошибка: {e}")
        print("Попробуйте перезапустить игру.")


if __name__ == "__main__":
    main()