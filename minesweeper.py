from tkinter import messagebox  # Импорт функциональности для вывода диалоговых окон
import tkinter as tk  # Импорт библиотеки для создания графического интерфейса
import random  # Импорт модуля для генерации случайных чисел
import struct  # Импорт модуля для упаковки и распаковки данных в бинарном формате
import math  # Импорт модуля для математических операций
import time  # Импорт модуля для работы со временем

CELL_SIZE = 36  # размер ячеек
BG_COLOR = "#222222"  # цвет заднего фона (темно-серый)
UNCLICKED_COLOR = "#d77f37"  # цвет не нажатых кнопок (оранжевый)
CLICKED_COLOR = "#222222"  # цвет нажатых/пустых ячеек (темно-серый)
NUMBER_COLORS = "#e3e3e3"  # цвет чисел (белый)
TEMP_BLANK_COLOR = "#aaaaaa"  # цвет соседних ячеек при нажатии на цифру (светло-серый)
IMPOSSIBLE_COLOR = "#503333"  # цвет невозможных ходов (красный)

class Minesweeper:
    def __init__(self, master):
        # Инициализация основных переменных и интерфейса игры
        self.master = master  # Ссылка на главное окно
        self.start_time = None  # Время начала игры
        self.game_active = False  # Флаг, показывающий, активна ли игра в данный момент
        self.buttons = []  # Список кнопок на игровом поле
        self.scheduled_tasks = []  # Список запланированных задач (таймеров)
        self.mines = set()  # Множество координат мин
        self.revealed = set()  # Множество координат открытых ячеек
        self.flags = set()  # Множество координат установленных флажков
        self.temp_blanks = set()  # Множество координат временных пустых ячеек
        self.first_click = True  # Флаг, показывающий, был ли совершен первый клик в игре
        self.master.configure(bg=BG_COLOR)  # Настройка фона главного окна
        self.show_menu()  # Отображение главного меню игры

    def recenter_window(self):
        # Обновление геометрии окна
        self.master.update_idletasks()
        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height()

        # Получение размеров экрана
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Вычисление координат для центрирования окна
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)

        # Установка новой геометрии окна для центрирования
        self.master.geometry(f'+{center_x}+{center_y}')

    def show_menu(self):
        # Создание фрейма меню
        self.menu_frame = tk.Frame(self.master, bg=BG_COLOR)
        self.menu_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Метка с заголовком
        title_label = tk.Label(self.menu_frame, text="Выбрать сложность", bg=BG_COLOR, fg=NUMBER_COLORS,
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        # Конфигурация уровней сложности
        modes = [
            ("Легкий", 13, 13, 10),
            ("Средний", 16, 16, 40),
            ("Сложный", 30, 16, 99)
        ]
        buttons_frame = tk.Frame(self.menu_frame, bg=BG_COLOR)
        buttons_frame.pack()

        # Создание кнопок для каждого уровня сложности
        for index, mode in enumerate(modes):
            btn = tk.Button(buttons_frame, text=mode[0], bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                            font=("Arial", 12, "bold"), relief="flat",
                            command=lambda m=mode: self.start_game(*m[1:]))
            btn.grid(row=0, column=index, padx=5, pady=5)

        # Дополнительные кнопки
        other_label = tk.Label(self.menu_frame, text="Другое", bg=BG_COLOR, fg=NUMBER_COLORS,
                               font=("Arial", 12, "bold"))
        other_label.pack(pady=(20, 5))

        highscores_btn = tk.Button(self.menu_frame, text="Рекорды", bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                                   font=("Arial", 12, "bold"), relief="flat",
                                   command=self.show_highscores)
        highscores_btn.pack(pady=(5, 5))

        help_btn = tk.Button(self.menu_frame, text="Помощь", bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                             font=("Arial", 12, "bold"), relief="flat", command=self.show_help)
        help_btn.pack(pady=(5, 5))

        # Центрирование окна
        self.recenter_window()

    def format_time(self, seconds):
        # Преобразование общего количества секунд в часы, минуты и секунды
        total_seconds = float(seconds)
        hours = int(total_seconds) // 3600
        minutes = (int(total_seconds) % 3600) // 60
        seconds = total_seconds % 60
        formatted_time = ""
        # Добавление часов к форматированному времени, если они присутствуют
        if hours > 0:
            formatted_time += f"{hours}ч "
        # Добавление минут к форматированному времени, если они присутствуют, или если есть часы
        if minutes > 0 or hours > 0:
            formatted_time += f"{minutes}м "
        # Добавление секунд с точностью до двух знаков после запятой к форматированному времени
        formatted_time += f"{seconds:.2f}с"
        return formatted_time

    def show_highscores(self):
        # Создание окна для отображения рекордов
        highscores_window = tk.Toplevel(self.master, bg=BG_COLOR)
        highscores_window.title("Рекорды")
        highscores_window.resizable(False, False)

        # Словарь с уровнями сложности и их описанием
        difficulties = {
            "Легкий": "9x9 - 10 Mines",
            "Средний": "16x16 - 40 Mines",
            "Сложный": "30x16 - 99 Mines"
        }

        # Создание фрейма для размещения рекордов
        highscores_frame = tk.Frame(highscores_window, bg=BG_COLOR)
        highscores_frame.pack(pady=(10, 5))

        # Отображение названий уровней сложности в верхней части окна
        for index, difficulty in enumerate(difficulties.keys()):
            tk.Label(highscores_frame, text=difficulty, bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", 16, "bold")).grid(
                row=0, column=index, padx=20)

        # Чтение рекордов из файла
        records = []
        try:
            with open("minesweeper.wins", "rb") as file:
                while True:
                    length_bytes = file.read(4)
                    if not length_bytes:
                        break  # Конец файла
                    length = struct.unpack('I', length_bytes)[0]
                    mode_bytes = file.read(length)
                    mode = mode_bytes.decode('utf-8')
                    time_taken_bytes = file.read(4)
                    time_taken = struct.unpack('f', time_taken_bytes)[0]
                    records.append((mode, time_taken))
        except FileNotFoundError:
            pass

        # Сортировка рекордов по времени
        records.sort(key=lambda x: float(x[1]))

        # Группировка рекордов по уровням сложности
        records_by_difficulty = {difficulty: [] for difficulty in difficulties.keys()}
        for record in records:
            for difficulty, format in difficulties.items():
                if format in record[0]:
                    records_by_difficulty[difficulty].append(record)
                    break

        # Отображение топ-5 рекордов для каждого уровня сложности
        for index, (difficulty, records) in enumerate(records_by_difficulty.items()):
            if not records:
                tk.Label(highscores_frame, text="Нет рекорда!", bg=BG_COLOR, fg=NUMBER_COLORS).grid(row=1,
                                                                                                    column=index,
                                                                                                    padx=20)
                continue
            top_records = records[:5]
            for row, record in enumerate(top_records, start=1):
                # Форматирование времени и его отображение в соответствующей ячейке
                formatted_time = self.format_time(record[1])
                tk.Label(highscores_frame, text=formatted_time, bg=BG_COLOR, fg=NUMBER_COLORS).grid(row=row,
                                                                                                    column=index,
                                                                                                    padx=20)

        # Обновление размеров окна и центрирование его на экране
        highscores_window.update_idletasks()

        window_width = highscores_window.winfo_width()
        window_height = highscores_window.winfo_height()

        screen_width = highscores_window.winfo_screenwidth()
        screen_height = highscores_window.winfo_screenheight()

        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)

        highscores_window.geometry(f'+{center_x}+{center_y}')

    def show_help(self):
        # Создание окна справки
        help_window = tk.Toplevel(self.master, bg=BG_COLOR)
        help_window.title("Помощь")
        help_window.resizable(False, False)

        # Текст инструкций
        instructions = """
        Добро пожаловать в Сапер!

        Цель:
        Цель состоит в том, чтобы обнаружить все ячейки, в которых нет мин.
        Если вы обнаружите мину, вы проиграете.

        Управление:
        - Щелкните левой кнопкой мыши, чтобы открыть ячейку.
        - Щелкните правой кнопкой мыши, чтобы установить или удалить флажок в ячейке.
        - Зажмите левую кнопку мыши на цифре, чтобы посмотреть соседей ячейки.

        Подсказки:
        - Первое нажатие всегда безопасен.
        - Используйте цифры, чтобы определить, где расположены мины.

        Удачи!  
        """

        # Создание метки с инструкциями
        help_label = tk.Label(help_window, text=instructions, bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", 12))
        help_label.pack(padx=20, pady=20)

        # Кнопка "OK"
        ok_button = tk.Button(help_window, text="OK", bg=UNCLICKED_COLOR, fg=NUMBER_COLORS, font=("Arial", 12, "bold"),
                              command=help_window.destroy)
        ok_button.pack(pady=(0, 20))

        # Обновление размеров окна и центрирование его на экране
        help_window.update_idletasks()
        window_width = help_window.winfo_width()
        window_height = help_window.winfo_height()
        screen_width = help_window.winfo_screenwidth()
        screen_height = help_window.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        help_window.geometry(f'+{center_x}+{center_y}')

    def show_main_menu(self):
        # Открытие главного меню
        self.master.destroy()
        main()

    def start_game(self, width, height, mines):
        # Установка размеров поля и количества мин
        global GRID_WIDTH, GRID_HEIGHT, MINES_COUNT
        GRID_WIDTH, GRID_HEIGHT, MINES_COUNT = width, height, mines

        # Удаление фрейма меню
        self.menu_frame.destroy()

        # Создание двумерного списка для хранения кнопок игрового поля
        self.buttons = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Создание кнопок для игрового поля
        self.create_widgets()

        # Центрирование окна
        self.recenter_window()

    def create_widgets(self):
        # Создание фрейма для отображения информации о количестве флажков и времени
        self.info_frame = tk.Frame(self.master, bg=BG_COLOR, height=CELL_SIZE)
        self.info_frame.grid(row=0, column=0, columnspan=GRID_WIDTH, sticky="nsew")

        # Создание метки для отображения количества установленных флажков
        self.flag_counter_label = tk.Label(self.info_frame, text=f"Флажков: 0/{MINES_COUNT}", bg=BG_COLOR,
                                           fg=NUMBER_COLORS, font=("Arial", int(CELL_SIZE / 2.5), "bold"))
        self.flag_counter_label.pack(side="left", padx=(10, 0))

        # Создание кнопки "Заново"
        self.restart_button = tk.Button(self.info_frame, text="Заново", bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                                        font=("Arial", int(CELL_SIZE / 2.5), "bold"), relief="flat",
                                        command=self.restart_game)
        self.restart_button.pack(side="left", expand=True, padx=10)  # Добавлено отступление для визуального разделения

        # Создание кнопки "Меню"
        self.menu_button = tk.Button(self.info_frame, text="Меню", bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                                     font=("Arial", int(CELL_SIZE / 2.5), "bold"), relief="flat",
                                     command=self.show_main_menu)
        self.menu_button.pack(side="left", expand=True, padx=10)

        # Создание метки для отображения прошедшего времени
        self.time_elapsed_label = tk.Label(self.info_frame, text="Время: 0с", bg=BG_COLOR, fg=NUMBER_COLORS,
                                           font=("Arial", int(CELL_SIZE / 2.5), "bold"))
        self.time_elapsed_label.pack(side="right", padx=(0, 10))

        # Создание кнопок-клеток игрового поля
        for row in range(1, GRID_HEIGHT + 1):  # Размещение кнопок начиная со второй строки
            for col in range(GRID_WIDTH):
                button = tk.Canvas(self.master, width=CELL_SIZE, height=CELL_SIZE, bg=UNCLICKED_COLOR,
                                   highlightthickness=0)
                button.grid(row=row, column=col, sticky="nsew")
                # Привязка событий к кнопкам
                button.bind("<Button-1>", lambda e, r=row, c=col: self.cell_click(r - 1, c, e))
                button.bind("<ButtonRelease-1>", lambda e, r=row, c=col: self.hide_temporary_blanks(r - 1, c, e))
                button.bind("<Button-3>", lambda e, r=row, c=col: self.place_flag(r - 1, c))
                button.bind("<Enter>", lambda e, r=row, c=col: self.on_hover(e, r - 1, c))
                button.bind("<Leave>", lambda e, r=row, c=col: self.on_leave(e, r - 1, c))
                self.buttons[row - 1][col] = button

    def restart_game(self):
        # Отмена всех запланированных задач
        for task_id in self.scheduled_tasks:
            self.master.after_cancel(task_id)
        self.scheduled_tasks.clear()  # Очистка списка идентификаторов задач

        # Очистка текущего состояния игры
        for row in self.buttons:
            for button in row:
                button.destroy()
        self.buttons.clear()
        self.mines.clear()
        self.revealed.clear()
        self.flags.clear()
        self.temp_blanks.clear()
        self.first_click = True
        self.game_active = False
        # Начало новой игры с теми же настройками
        self.start_game(GRID_WIDTH, GRID_HEIGHT, MINES_COUNT)


    def place_flag(self, row, col, event=None):
        # Если это первый клик или клетка уже открыта, прервать выполнение функции
        if self.first_click or (row, col) in self.revealed:
            return
        button = self.buttons[row][col]
        if (row, col) in self.flags:  # Если флажок уже установлен, удалить его
            self.flags.remove((row, col))
            button.delete("flag")  # Удалить изображение флага с кнопки
            button.config(bg=UNCLICKED_COLOR)  # Вернуть цвет клетки по умолчанию
            self.on_hover(None, row, col)  # Показать подсказку при наведении на кнопку
        else:
            self.flags.add((row, col))  # Добавить координаты клетки в множество установленных флажков
            button.config(bg="#666666")  # Изменить цвет клетки на серый для обозначения флага
            self.draw_flag(button)  # Нарисовать изображение флага на кнопке
            self.on_hover(None, row, col)  # Показать подсказку при наведении на кнопку

        self.update_flag_counter()  # Обновить счетчик флажков
        self.update_adjacent_cells_status(row, col)  # Обновить статус смежных клеток

    def cell_click(self, row, col, event):
        if self.first_click:  # Если это первый клик
            # Установить флаг первого клика как False и начать отсчет времени
            self.first_click = False
            self.start_time = time.time()
            self.game_active = True
            self.update_time_elapsed()  # Обновить отображение времени на экране
            # Разместить мины после первого клика и открыть клетку, на которой был сделан первый клик
            self.place_mines(row, col)
            self.reveal_cell(row, col)
        elif (row, col) not in self.flags and (row, col) not in self.revealed:
            if (row, col) in self.mines:  # Если на клетке есть мина
                self.game_over(False)  # Игра заканчивается поражением
            else:
                self.reveal_cell(row, col)  # Открыть клетку
                if self.check_win():  # Проверить, выиграна ли игра
                    self.game_over(True)  # Если да, завершить игру с победой
        elif (row, col) in self.revealed:
            self.chord_or_show_temp_blanks(row, col)  # Открыть соседние клетки или показать временные пустоты

    def reveal_cell(self, row, col):
        # Инициализация очереди для BFS (поиск в ширину)
        queue = [(row, col)]
        while queue:
            current_row, current_col = queue.pop(0)
            # Если клетка уже открыта или на ней установлен флаг, пропустить ее
            if (current_row, current_col) in self.revealed or (current_row, current_col) in self.flags:
                continue
            # Добавить клетку в множество открытых клеток
            self.revealed.add((current_row, current_col))
            button = self.buttons[current_row][current_col]

            # Анимация изменения цвета клетки от UNCLICKED_COLOR к CLICKED_COLOR
            steps = 10
            for i in range(steps + 1):
                factor = i / steps
                color = self.interpolate_color(UNCLICKED_COLOR, CLICKED_COLOR, factor)  # Интерполяция цвета
                # Запланировать задачу изменения цвета клетки через некоторое время
                task_id = self.master.after(int(i * 50), lambda b=button, c=color: b.config(bg=c))
                self.scheduled_tasks.append(task_id)

            # Подсчет количества мин в соседних клетках
            mines_count = self.adjacent_mines(current_row, current_col)
            if mines_count == 0:
                # Если рядом с клеткой нет мин, добавить соседние клетки в очередь для дальнейшего открытия
                for r in range(max(0, current_row - 1), min(GRID_HEIGHT, current_row + 2)):
                    for c in range(max(0, current_col - 1), min(GRID_WIDTH, current_col + 2)):
                        if (r, c) not in self.revealed and (r, c) not in self.flags:
                            queue.append((r, c))
            else:
                # Если рядом с клеткой есть мины, отобразить количество мин на клетке
                self.master.after(steps * 10,
                                  lambda b=button, mc=mines_count: b.create_text(CELL_SIZE // 2, CELL_SIZE // 2,
                                                                                 text=str(mc), fill=NUMBER_COLORS,
                                                                                 font=("Arial", int(CELL_SIZE / 2.7),
                                                                                       "bold")))

    def update_flag_counter(self, flags=None):
        # Если количество флажков не указано, оно равно текущему количеству установленных флажков
        if flags is None:
            flags = len(self.flags)
        # Обновление текста метки счетчика флажков
        self.flag_counter_label.config(text=f"Flagged: {flags}/{MINES_COUNT}")

    def draw_flag(self, button):
        # Цвет флага
        flag_color = BG_COLOR
        # Общая ширина флага и его высота
        total_flag_width = CELL_SIZE / 3
        flag_height = CELL_SIZE / 3
        # Толщина линий
        line_thickness = flag_height / 5
        # Размеры квадрата и прямоугольника на флаге
        square_side = flag_height / 2
        rectangle_height = square_side
        rectangle_length = square_side * 0.8
        rectangle_y_offset = square_side * 0.3

        # Координаты начала рисования каждой части флага
        flag_x_start = (CELL_SIZE - total_flag_width) / 2
        line_y_start = (CELL_SIZE - flag_height) / 2
        square_x_start = flag_x_start + line_thickness
        rectangle_x_start = square_x_start + square_side
        rectangle_y_start = line_y_start + rectangle_y_offset

        # Рисование вертикальной линии
        button.create_rectangle(flag_x_start, line_y_start, flag_x_start + line_thickness, line_y_start + flag_height,
                                tags="flag", fill=flag_color, outline=flag_color)
        # Рисование квадрата
        button.create_rectangle(square_x_start, line_y_start, square_x_start + square_side, line_y_start + square_side,
                                tags="flag", fill=flag_color, outline=flag_color)
        # Рисование прямоугольника
        button.create_rectangle(rectangle_x_start, rectangle_y_start, rectangle_x_start + rectangle_length,
                                rectangle_y_start + rectangle_height, tags="flag", fill=flag_color, outline=flag_color)

    def update_adjacent_cells_status(self, row, col):
        # Обновление статуса соседних ячеек вокруг ячейки с координатами (row, col)
        for r in range(max(0, row - 1), min(GRID_HEIGHT, row + 2)):
            for c in range(max(0, col - 1), min(GRID_WIDTH, col + 2)):
                # Проверка, является ли соседняя ячейка ранее открытой
                if (r, c) in self.revealed:
                    # Получение количества мин вокруг соседней ячейки
                    num = self.adjacent_mines(r, c)
                    # Подсчет количества флажков вокруг соседней ячейки
                    flags_around = sum(
                        (rr, cc) in self.flags for rr in range(max(0, r - 1), min(GRID_HEIGHT, r + 2)) for cc in
                        range(max(0, c - 1), min(GRID_WIDTH, c + 2)))
                    # Если количество флажков вокруг превышает количество мин, окрасить ячейку в цвет невозможного
                    if flags_around > num:
                        self.buttons[r][c].config(bg=IMPOSSIBLE_COLOR)
                    # Иначе окрасить ячейку в цвет открытой
                    else:
                        self.buttons[r][c].config(bg=CLICKED_COLOR)

    def adjacent_mines(self, row, col):
        # Возвращает количество мин, соседствующих с ячейкой по координатам (row, col)
        return sum((r, c) in self.mines for r in range(max(0, row - 1), min(GRID_HEIGHT, row + 2)) for c in
                   range(max(0, col - 1), min(GRID_WIDTH, col + 2)))

    def fade_out_cell(self, button, steps, final_color, callback=None):
        # Плавное затухание цвета ячейки кнопки
        current_color = button.cget('bg')  # Текущий цвет кнопки
        r1, g1, b1 = self.master.winfo_rgb(current_color)  # Конвертация текущего цвета в RGB
        r2, g2, b2 = self.master.winfo_rgb(final_color)  # Конвертация конечного цвета в RGB

        # Рассчитываем изменение компонент цвета для каждого шага анимации
        delta_r = (r2 - r1) / steps
        delta_g = (g2 - g1) / steps
        delta_b = (b2 - b1) / steps

        # Внутренняя функция для выполнения анимации затухания
        def fade(step=0):
            nonlocal r1, g1, b1  # Используем nonlocal, чтобы изменять значения переменных из внешней области видимости
            if step < steps:
                # Вычисляем новые значения компонент цвета
                r1, g1, b1 = r1 + delta_r, g1 + delta_g, b1 + delta_b
                # Формируем новый цвет на основе новых значений RGB
                next_color = f'#{int(r1 / 256):02x}{int(g1 / 256):02x}{int(b1 / 256):02x}'
                # Применяем новый цвет к кнопке
                button.config(bg=next_color)
                # Запускаем следующий шаг анимации через 25 миллисекунд
                self.master.after(25, lambda: fade(step + 1))
            else:
                # Если достигнут последний шаг анимации, вызываем обратный вызов (если он был предоставлен)
                if callback:
                    callback()

        # Запускаем анимацию затухания
        fade()

    def interpolate_color(self, start_color, end_color, factor):
        # Интерполирует цвет между начальным и конечным цветами с заданным коэффициентом
        start_r, start_g, start_b = self.master.winfo_rgb(start_color)  # Получаем компоненты RGB начального цвета
        end_r, end_g, end_b = self.master.winfo_rgb(end_color)  # Получаем компоненты RGB конечного цвета

        # Вычисляем новые значения компонент цвета на основе коэффициента интерполяции
        r = int(start_r + (end_r - start_r) * factor)
        g = int(start_g + (end_g - start_g) * factor)
        b = int(start_b + (end_b - start_b) * factor)

        # Формируем новый цвет в формате HEX
        return f'#{r >> 8:02x}{g >> 8:02x}{b >> 8:02x}'

    def game_over(self, win):
        # Устанавливает флаг окончания игры и блокирует кнопки на игровом поле
        self.game_active = False

        # Удаляет все привязки к кнопкам для предотвращения дальнейших действий игрока
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                self.buttons[row][col].unbind("<Button-1>")
                self.buttons[row][col].unbind("<Button-3>")
                self.buttons[row][col].unbind("<Enter>")
                self.buttons[row][col].unbind("<Leave>")

        # Если игра закончилась поражением
        if not win:
            # Отображает все мины и неверно установленные флаги
            for r, c in self.mines:
                if (r, c) not in self.flags:
                    button = self.buttons[r][c]
                    button.config(bg=UNCLICKED_COLOR)
                    self.draw_mine(button)

            # Показывает все ячейки, которые не были открыты
            for row in range(GRID_HEIGHT):
                for col in range(GRID_WIDTH):
                    if (row, col) not in self.mines:
                        self.reveal_cell(row, col)
        # Если игра закончилась победой
        else:
            # Отображает все мины, если они не помечены флагами
            for r, c in self.mines:
                if (r, c) not in self.flags:
                    button = self.buttons[r][c]
                    button.config(bg="#666666")
                    self.draw_flag(button)

            # Обновляет счетчик флагов до общего количества мин
            self.update_flag_counter(MINES_COUNT)

        # Выводит сообщение о победе или поражении и, при победе, сохраняет рекорд
        if win:
            end_time = time.time()
            time_taken = end_time - self.start_time
            self.store_win_record(time_taken)
            messagebox.showinfo("Сапер", "Поздравляем! Ты выиграл!")
        else:
            messagebox.showinfo("Сапер", "Сожалеем. Ты проиграл.")

    def on_hover(self, event, row, col):
        # Проверка, является ли ячейка непоказанной
        if (row, col) not in self.revealed:
            # Проверка, установлен ли флажок в ячейке
            if (row, col) in self.flags:
                # Изменение цвета кнопки на серый
                self.buttons[row][col].config(bg="#7e7e7e")
            else:
                # Изменение цвета кнопки при наведении на оранжевый
                self.buttons[row][col].config(bg="#e89b53")

    def on_leave(self, event, row, col):
        # Проверка, является ли ячейка непоказанной
        if (row, col) not in self.revealed:
            # Проверка, установлен ли флажок в ячейке
            if (row, col) in self.flags:
                # Изменение цвета кнопки на серый при уходе курсора
                self.buttons[row][col].config(bg="#666666")
            else:
                # Изменение цвета кнопки на изначальный цвет при уходе курсора
                self.buttons[row][col].config(bg=UNCLICKED_COLOR)

    def update_time_elapsed(self):
        # Проверка, активна ли игра
        if self.game_active:
            # Вычисление прошедшего времени с начала игры
            elapsed_time = int(time.time() - self.start_time)

            # Обновление метки времени на интерфейсе
            self.time_elapsed_label.config(text=f"Время: {elapsed_time}c")

            # Запуск этого метода повторно через 100 миллисекунд
            self.master.after(100, self.update_time_elapsed)

    def chord_or_show_temp_blanks(self, row, col):
        # Определение числа мин вокруг ячейки
        num = self.adjacent_mines(row, col)

        # Определение числа флажков вокруг ячейки
        flags_around = sum(
            (r, c) in self.flags
            for r in range(max(0, row - 1), min(GRID_HEIGHT, row + 2))
            for c in range(max(0, col - 1), min(GRID_WIDTH, col + 2))
        )

        # Если число мин вокруг ячейки равно числу флажков вокруг неё
        if num == flags_around:
            # Открытие всех нефлажкованных ячеек вокруг текущей ячейки
            for r in range(max(0, row - 1), min(GRID_HEIGHT, row + 2)):
                for c in range(max(0, col - 1), min(GRID_WIDTH, col + 2)):
                    if (r, c) not in self.flags:
                        # Если обнаружена мина, игра заканчивается
                        if (r, c) in self.mines:
                            self.game_over(False)
                            return
                        self.reveal_cell(r, c)

            # Проверка на победу после открытия ячеек
            if self.check_win():
                self.game_over(True)

        # Если число флажков превышает число мин вокруг ячейки
        elif flags_around > num:
            self.buttons[row][col].config(bg=IMPOSSIBLE_COLOR)

        # В противном случае показ временных пустых ячеек вокруг ячейки
        else:
            self.show_temporary_blanks(row, col)

    def show_temporary_blanks(self, row, col):
        # Перебор всех соседних ячеек вокруг указанной ячейки
        for r in range(max(0, row - 1), min(GRID_HEIGHT, row + 2)):
            for c in range(max(0, col - 1), min(GRID_WIDTH, col + 2)):
                # Если ячейка не была открыта и не помечена флажком
                if (r, c) not in self.revealed and (r, c) not in self.flags:
                    # Изменение цвета кнопки этой ячейки на цвет временных пустых ячеек
                    self.buttons[r][c].config(bg=TEMP_BLANK_COLOR)
                    # Добавление ячейки во временные пустые ячейки
                    self.temp_blanks.add((r, c))

    def hide_temporary_blanks(self, row, col, event):
        # Перебор всех временных пустых ячеек
        for r, c in self.temp_blanks:
            # Восстановление исходного цвета кнопки этой ячейки
            self.buttons[r][c].config(bg=UNCLICKED_COLOR)
        # Очистка множества временных пустых ячеек
        self.temp_blanks.clear()

    def place_mines(self, start_row, start_col):
        # Определение безопасной зоны вокруг начального хода
        safe_zone = {(start_row + i, start_col + j) for i in range(-1, 2) for j in range(-1, 2)}

        # Добавление мин на поле, пока не будет достигнуто требуемое количество мин
        while len(self.mines) < MINES_COUNT:
            # Генерация случайной позиции для мины
            r, c = random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1)
            # Проверка, что мина не попадает в безопасную зону и не повторяется
            if (r, c) not in safe_zone and (r, c) not in self.mines:
                # Добавление мины на поле
                self.mines.add((r, c))

    def check_win(self):
        # Проверка, что количество открытых ячеек равно общему числу ячеек минус количество мин
        if len(self.revealed) == GRID_WIDTH * GRID_HEIGHT - MINES_COUNT:
            return True
        return False

    def store_win_record(self, time_taken):
        # Формирование строки режима и его кодирование в байты
        mode = f"{GRID_WIDTH}x{GRID_HEIGHT} - {MINES_COUNT} Mines"
        mode_encoded = mode.encode('utf-8')

        # Упаковка рекорда в бинарный формат
        record = struct.pack('I', len(mode_encoded)) + mode_encoded + struct.pack('f', time_taken)

        # Запись рекорда в файл
        with open("minesweeper.wins", "ab") as file:
            file.write(record)

    def draw_mine(self, button):
        # Определение размеров внешнего и внутреннего кругов, а также размера ножки мины
        outer_circle_radius = CELL_SIZE * 0.2
        inner_circle_radius = CELL_SIZE * 0.07
        leg_size = CELL_SIZE * 0.1

        # Нарисовать внешний круг мины
        button.create_oval(
            CELL_SIZE / 2 - outer_circle_radius, CELL_SIZE / 2 - outer_circle_radius,
            CELL_SIZE / 2 + outer_circle_radius, CELL_SIZE / 2 + outer_circle_radius,
            fill=BG_COLOR, outline=BG_COLOR
        )

        # Нарисовать внутренний круг мины
        button.create_oval(
            CELL_SIZE / 2 - inner_circle_radius, CELL_SIZE / 2 - inner_circle_radius,
            CELL_SIZE / 2 + inner_circle_radius, CELL_SIZE / 2 + inner_circle_radius,
            fill=UNCLICKED_COLOR, outline=UNCLICKED_COLOR
        )

        # Нарисовать ножки мины
        for angle in range(0, 360, 45):
            radian = angle * (math.pi / 180)

            x_center = CELL_SIZE / 2 + (outer_circle_radius + leg_size / 2) * math.cos(radian)
            y_center = CELL_SIZE / 2 + (outer_circle_radius + leg_size / 2) * math.sin(radian)

            x = x_center - leg_size / 2
            y = y_center - leg_size / 2
            button.create_rectangle(
                x, y, x + leg_size, y + leg_size,
                fill=BG_COLOR, outline=BG_COLOR
            )


def main():
    # Создание главного окна
    root = tk.Tk()
    root.title("Сапер")
    root.resizable(False, False)

    # Обновление геометрии окна для центрирования на экране
    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    root.geometry(f'+{center_x}+{center_y}')

    # Создание экземпляра игры "Minesweeper"
    game = Minesweeper(root)

    # Запуск главного цикла игры
    root.mainloop()



if __name__ == "__main__":
    main()