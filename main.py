import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime


class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.history_file = "quote_history.json"

        self.quotes = [
            {"text": "Будь изменением, которое ты хочешь видеть в мире.", "author": "Махатма Ганди",
             "topic": "Мотивация"},
            {"text": "Жизнь - это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон",
             "topic": "Жизнь"},
            {"text": "Не количество прожитых лет важно, а качество.", "author": "Авраам Линкольн", "topic": "Мудрость"},
            {"text": "Единственный способ делать великую работу - любить то, что ты делаешь.", "author": "Стив Джобс",
             "topic": "Карьера"},
            {"text": "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма.",
             "author": "Уинстон Черчилль", "topic": "Мотивация"},
            {"text": "Сложнее всего начать действовать, все остальное зависит от упорства.", "author": "Амелия Эрхарт",
             "topic": "Мотивация"},
            {"text": "Знание - сила.", "author": "Фрэнсис Бэкон", "topic": "Образование"},
            {"text": "Время - деньги.", "author": "Бенджамин Франклин", "topic": "Время"},
            {"text": "Человек, который не совершал ошибок, никогда не пробовал ничего нового.",
             "author": "Альберт Эйнштейн", "topic": "Мудрость"}
        ]

        self.history = []
        self.load_history()

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        quote_frame = ttk.LabelFrame(main_frame, text="Текущая цитата", padding="10")
        quote_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.current_quote_text = tk.StringVar()
        self.current_quote_author = tk.StringVar()

        quote_display = ttk.Label(quote_frame, textvariable=self.current_quote_text,
                                  wraplength=700, font=("Arial", 12, "italic"))
        quote_display.grid(row=0, column=0, pady=5)

        author_display = ttk.Label(quote_frame, textvariable=self.current_quote_author,
                                   font=("Arial", 10))
        author_display.grid(row=1, column=0, sticky=tk.E)

        generate_btn = ttk.Button(main_frame, text="Сгенерировать цитату",
                                  command=self.generate_quote)
        generate_btn.grid(row=1, column=0, columnspan=2, pady=10)

        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(filter_frame, text="Фильтр по автору:").grid(row=0, column=0, padx=5)
        self.author_filter = ttk.Combobox(filter_frame, values=self.get_authors(), width=30)
        self.author_filter.grid(row=0, column=1, padx=5)
        self.author_filter.bind('<<ComboboxSelected>>', self.apply_filters)

        ttk.Button(filter_frame, text="Очистить фильтр",
                   command=self.clear_filters).grid(row=0, column=2, padx=5)

        ttk.Label(filter_frame, text="Фильтр по теме:").grid(row=1, column=0, padx=5)
        self.topic_filter = ttk.Combobox(filter_frame, values=self.get_topics(), width=30)
        self.topic_filter.grid(row=1, column=1, padx=5)
        self.topic_filter.bind('<<ComboboxSelected>>', self.apply_filters)

        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую цитату", padding="10")
        add_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(add_frame, text="Текст цитаты:").grid(row=0, column=0, sticky=tk.W)
        self.new_quote_text = tk.Text(add_frame, height=3, width=60)
        self.new_quote_text.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Label(add_frame, text="Автор:").grid(row=2, column=0, sticky=tk.W)
        self.new_quote_author = ttk.Entry(add_frame, width=30)
        self.new_quote_author.grid(row=2, column=1, sticky=tk.W, padx=5)

        ttk.Label(add_frame, text="Тема:").grid(row=3, column=0, sticky=tk.W)
        self.new_quote_topic = ttk.Entry(add_frame, width=30)
        self.new_quote_topic.grid(row=3, column=1, sticky=tk.W, padx=5)

        ttk.Button(add_frame, text="Добавить цитату",
                   command=self.add_quote).grid(row=4, column=0, columnspan=2, pady=10)

        history_frame = ttk.LabelFrame(main_frame, text="История цитат", padding="10")
        history_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        columns = ("text", "author", "topic", "timestamp")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        self.history_tree.heading("text", text="Цитата")
        self.history_tree.heading("author", text="Автор")
        self.history_tree.heading("topic", text="Тема")
        self.history_tree.heading("timestamp", text="Время")

        self.history_tree.column("text", width=400)
        self.history_tree.column("author", width=150)
        self.history_tree.column("topic", width=100)
        self.history_tree.column("timestamp", width=150)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(history_buttons_frame, text="Очистить историю",
                   command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_buttons_frame, text="Сохранить историю",
                   command=self.save_history).pack(side=tk.LEFT, padx=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        self.update_history_display()

    def get_authors(self):
        authors = set(quote["author"] for quote in self.quotes)
        return sorted(list(authors))

    def get_topics(self):
        topics = set(quote["topic"] for quote in self.quotes)
        return sorted(list(topics))

    def generate_quote(self):
        author_filter = self.author_filter.get()
        topic_filter = self.topic_filter.get()

        filtered_quotes = self.quotes.copy()

        if author_filter and author_filter != "":
            filtered_quotes = [q for q in filtered_quotes if q["author"] == author_filter]

        if topic_filter and topic_filter != "":
            filtered_quotes = [q for q in filtered_quotes if q["topic"] == topic_filter]

        if not filtered_quotes:
            messagebox.showwarning("Нет цитат", "Нет цитат, соответствующих выбранным фильтрам!")
            return

        selected_quote = random.choice(filtered_quotes)

        self.current_quote_text.set(f'"{selected_quote["text"]}"')
        self.current_quote_author.set(f'"— {selected_quote["author"]} (Тема: {selected_quote["topic"]})"')

        history_entry = {
            "text": selected_quote["text"],
            "author": selected_quote["author"],
            "topic": selected_quote["topic"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        self.update_history_display()
        self.save_history()

    def add_quote(self):
        text = self.new_quote_text.get("1.0", tk.END).strip()
        author = self.new_quote_author.get().strip()
        topic = self.new_quote_topic.get().strip()

        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return
        if not topic:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return

        new_quote = {
            "text": text,
            "author": author,
            "topic": topic
        }
        self.quotes.append(new_quote)

        self.new_quote_text.delete("1.0", tk.END)
        self.new_quote_author.delete(0, tk.END)
        self.new_quote_topic.delete(0, tk.END)

        self.update_comboboxes()

        messagebox.showinfo("Успех", "Цитата успешно добавлена!")

    def apply_filters(self, event=None):
        pass

    def clear_filters(self):
        self.author_filter.set("")
        self.topic_filter.set("")
        messagebox.showinfo("Фильтры", "Фильтры очищены!")

    def update_comboboxes(self):
        self.author_filter['values'] = self.get_authors()
        self.topic_filter['values'] = self.get_topics()

    def update_history_display(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for entry in reversed(self.history):
            self.history_tree.insert("", 0, values=(
                entry["text"],
                entry["author"],
                entry["topic"],
                entry["timestamp"]
            ))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_history_display()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена!")

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as file:
                json.dump(self.history, file, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as file:
                    self.history = json.load(file)
            except Exception as e:
                print(f"Не удалось загрузить историю: {str(e)}")
                self.history = []


def main():
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()