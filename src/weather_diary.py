import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary — Дневник погоды")
        self.records_file = "data/weather_records.json"
        self.records = self.load_records()

        self.create_widgets()
        self.update_records_table()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.date_entry = tk.Entry(self.root, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.root, text="Температура (°C):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.temp_entry = tk.Entry(self.root, width=20)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.root, text="Описание погоды:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.desc_entry = tk.Entry(self.root, width=40)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.root, text="Осадки:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.precipitation_var = tk.StringVar(value="Нет")
        tk.Radiobutton(self.root, text="Да", variable=self.precipitation_var, value="Да").grid(row=3, column=1, sticky="w")
        tk.Radiobutton(self.root, text="Нет", variable=self.precipitation_var, value="Нет").grid(row=3, column=1, sticky="e")

        # Кнопка добавления
        self.add_button = tk.Button(self.root, text="Добавить запись", command=self.add_record)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Фильтры
        tk.Label(self.root, text="Фильтр по дате:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.filter_date_entry = tk.Entry(self.root, width=20)
        self.filter_date_entry.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.root, text="Фильтр по температуре (>):").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.filter_temp_entry = tk.Entry(self.root, width=20)
        self.filter_temp_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")

        self.apply_filter_button = tk.Button(self.root, text="Применить фильтры", command=self.apply_filters)
        self.apply_filter_button.grid(row=7, column=0, columnspan=2, pady=5)

        # Таблица записей
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")

        # Кнопки сохранения и загрузки
        self.save_button = tk.Button(self.root, text="Сохранить в JSON", command=self.save_records)
        self.save_button.grid(row=9, column=0, pady=5)

        self.load_button = tk.Button(self.root, text="Загрузить из JSON", command=self.load_records_from_file)
        self.load_button.grid(row=9, column=1, pady=5)

        # Настройка растягивания
        self.root.grid_rowconfigure(8, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def validate_input(self):
        """Проверка корректности ввода"""
        try:
            date_str = self.date_entry.get().strip()
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            return False

        try:
            temp = float(self.temp_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return False

        desc = self.desc_entry.get().strip()
        if not desc:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым.")
            return False

        return True

    def add_record(self):
        """Добавление новой записи"""
        if not self.validate_input():
            return

        record = {
            "date": self.date_entry.get().strip(),
            "temperature": float(self.temp_entry.get()),
            "description": self.desc_entry.get().strip(),
            "precipitation": self.precipitation_var.get()
        }

        self.records.append(record)
        self.update_records_table()
        self.clear_entries()

    def clear_entries(self):
        """Очистка полей ввода"""
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set("Нет")

    def update_records_table(self, records=None):
        """Обновление таблицы записей"""
        self.tree.delete(*self.tree.get_children())
        display_records = records if records is not None else self.records
        for record in display_records:
            self.tree.insert("", "end", values=(
                record["date"],
                f"{record['temperature']}°C",
                record["description"],
                record["precipitation"]
            ))

    def apply_filters(self):
        """Применение фильтров"""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered_records = self.records

        if filter_date:
            filtered_records = [r for r in filtered_records if r["date"] == filter_date]

        if filter_temp_str:
            try:
                filter_temp = float(filter_temp_str)
                filtered_records = [r for r in filtered_records if r["temperature"]
