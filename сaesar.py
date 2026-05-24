import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

RUS_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ENG_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

RUS_FREQUENCIES = {
    'а': 0.062, 'б': 0.014, 'в': 0.038, 'г': 0.013, 'д': 0.025,
    'е': 0.072, 'ж': 0.007, 'з': 0.016, 'и': 0.062, 'й': 0.010,
    'к': 0.028, 'л': 0.035, 'м': 0.026, 'н': 0.053, 'о': 0.090,
    'п': 0.023, 'р': 0.040, 'с': 0.045, 'т': 0.053, 'у': 0.021,
    'ф': 0.002, 'х': 0.009, 'ц': 0.003, 'ч': 0.012, 'ш': 0.006,
    'щ': 0.003, 'ъ': 0.014, 'ы': 0.016, 'ь': 0.014, 'э': 0.003,
    'ю': 0.006, 'я': 0.018
}

MIXED_ALPHABETS_ERROR = (
    "Ошибка: Текст содержит буквы двух алфавитов! "
    "Используйте только русский или только английский текст."
)


def has_mixed_alphabets(text):
    """Проверяет, содержит ли текст одновременно и русские, и английские буквы"""
    has_rus = False
    has_eng = False
    for char in text.lower().replace("ё", "е"):
        if char in RUS_ALPHABET:
            has_rus = True
        elif char in ENG_ALPHABET:
            has_eng = True
        if has_rus and has_eng:
            return True
    return False


def detect_alphabet(text):
    """Определяет алфавит текста (русский или английский) по первой найденной букве"""
    if has_mixed_alphabets(text):
        return None
    for char in text.lower():
        if char in RUS_ALPHABET:
            return RUS_ALPHABET
        if char in ENG_ALPHABET:
            return ENG_ALPHABET
    return None


def char_to_index(char, alphabet):
    """Возвращает порядковый номер буквы в алфавите"""
    return alphabet.index(char)


def index_to_char(ind, alphabet):
    """Возвращает букву из алфавита по её индексу (с защитой от выхода за границы)"""
    return alphabet[ind % len(alphabet)]


def clean_text(text, alphabet):
    """Приводит текст к нижнему регистру, заменяет 'ё' на 'е' и удаляет все сторонние символы"""
    text = text.lower().replace("ё", "е")
    cleaned_text = ""
    for char in text:
        if char in alphabet:
            cleaned_text += char
    if not cleaned_text:
        return None
    return cleaned_text


def format_output(text, length):
    """Разбивает текст на блоки заданной длины"""
    return " ".join([text[i:i + length] for i in range(0, len(text), length)])


def is_error(result):
    """Проверяет, является ли результат выполнения функции строкой с ошибкой"""
    return isinstance(result, str) and result.startswith("Ошибка")


def caesar_encrypt(text, key):
    """Шифрует текст методом Цезаря со сдвигом на величину key"""
    if has_mixed_alphabets(text):
        return MIXED_ALPHABETS_ERROR
    alphabet = detect_alphabet(text)
    if not alphabet:
        return "Ошибка: Не удалось определить алфавит! Используйте русские или английские буквы."
    text = clean_text(text, alphabet)
    if not text:
        return "Ошибка: Текст пуст или не содержит букв выбранного алфавита!"
    try:
        shift = int(key) % len(alphabet)
    except (ValueError, TypeError):
        return "Ошибка: Ключ должен быть целым числом!"
    encrypted_result = ""
    for char in text:
        char_ind = char_to_index(char, alphabet)
        new_ind = (char_ind + shift) % len(alphabet)
        encrypted_result += index_to_char(new_ind, alphabet)
    return format_output(encrypted_result, 5)


def caesar_decrypt(ciphertext, key):
    """Расшифровывает текст, сдвигая символы в обратную сторону на величину key"""
    if has_mixed_alphabets(ciphertext):
        return MIXED_ALPHABETS_ERROR
    alphabet = detect_alphabet(ciphertext)
    if not alphabet:
        return "Ошибка: Не удалось определить алфавит! Используйте русские или английские буквы."
    ciphertext = clean_text(ciphertext, alphabet)
    if not ciphertext:
        return "Ошибка: Текст пуст или не содержит букв выбранного алфавита!"
    try:
        shift = int(key) % len(alphabet)
    except (ValueError, TypeError):
        return "Ошибка: Ключ должен быть целым числом!"
    decrypted_result = ""
    for char in ciphertext:
        char_ind = char_to_index(char, alphabet)
        new_ind = (char_ind - shift) % len(alphabet)
        decrypted_result += index_to_char(new_ind, alphabet)
    return format_output(decrypted_result, 5)


def get_frequencies(text):
    """Считает частоту появления каждой буквы в тексте"""
    n = len(text)
    if n == 0:
        return None
    frequencies_dict = {}
    for char in RUS_ALPHABET:
        frequencies_dict[char] = text.count(char) / n
    return frequencies_dict


def find_best_shift_mnk(text):
    """Ищет самый вероятный шаг сдвига по методу наименьших квадратов"""
    actual_freqs = get_frequencies(text)
    best_shift = 0
    min_sum_sq = float('inf')
    for shift in range(len(RUS_ALPHABET)):
        sum_sq = 0
        for i in range(len(RUS_ALPHABET)):
            p_i = RUS_FREQUENCIES[RUS_ALPHABET[i]]
            f_i = actual_freqs[RUS_ALPHABET[(i + shift) % len(RUS_ALPHABET)]]
            sum_sq += (p_i - f_i) ** 2
        if sum_sq < min_sum_sq:
            min_sum_sq = sum_sq
            best_shift = shift
    return best_shift


def crack_caesar(ciphertext):
    """Взламывает шифр, возвращая подобранный сдвиг и расшифрованный текст."""
    if has_mixed_alphabets(ciphertext):
        return None, MIXED_ALPHABETS_ERROR
    cleaned = clean_text(ciphertext, RUS_ALPHABET)
    if not cleaned:
        return None, "Ошибка: Текст пуст или не содержит русских букв!"
    if len(cleaned) < 50:
        return None, f"Ошибка: Для надежного взлома длина текста должна быть не менее 50 символов! (Сейчас букв: {len(cleaned)})"
    best_shift = find_best_shift_mnk(cleaned)
    decrypted = caesar_decrypt(cleaned, best_shift)
    if is_error(decrypted):
        return None, decrypted
    return best_shift, decrypted


def set_output(output_box, text):
    """Записывает результат в заблокированное для редактирования текстовое поле GUI."""
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text)
    output_box.config(state=tk.DISABLED)


def get_input(input_box):
    """Получает и очищает от пробелов по краям введенный пользователем текст из GUI"""
    return input_box.get("1.0", tk.END).strip()


def validate_key(key_entry):
    """Проверяет, ввел ли пользователь ключ в соответствующее поле ввода"""
    key = key_entry.get().strip()
    if not key:
        messagebox.showerror("Ошибка", "Введите ключ (число сдвига).")
        return None
    return key


def build_text_section(parent, input_label, output_label, with_key=True):
    """Конструирует стандартный блок интерфейса: поле ввода, поле вывода и (опционально) ключ"""
    ttk.Label(parent, text=input_label).pack(anchor="w")
    input_box = scrolledtext.ScrolledText(parent, height=6, wrap=tk.WORD, font=("Menlo", 11))
    input_box.pack(fill="both", expand=True, pady=(2, 8))
    key_entry = None
    if with_key:
        key_row = ttk.Frame(parent)
        key_row.pack(fill="x", pady=(0, 8))
        ttk.Label(key_row, text="Ключ (сдвиг):").pack(side="left")
        key_entry = ttk.Entry(key_row, width=12)
        key_entry.pack(side="left", padx=(8, 0))
    ttk.Label(parent, text=output_label).pack(anchor="w")
    output_box = scrolledtext.ScrolledText(
        parent, height=6, wrap=tk.WORD, font=("Menlo", 11), state=tk.DISABLED
    )
    output_box.pack(fill="both", expand=True, pady=(2, 8))
    return input_box, key_entry, output_box


def on_encrypt(enc_input, enc_key, enc_output):
    """Обработчик нажатия кнопки 'Зашифровать': собирает данные, шифрует и выводит результат"""
    text = get_input(enc_input)
    if not text:
        messagebox.showerror("Ошибка", "Введите текст для шифрования.")
        return
    key = validate_key(enc_key)
    if key is None:
        return
    result = caesar_encrypt(text, key)
    if is_error(result):
        messagebox.showerror("Ошибка", result.replace("Ошибка: ", "", 1))
        return
    set_output(enc_output, result)


def on_decrypt(dec_input, dec_key, dec_output):
    """Обработчик нажатия кнопки 'Расшифровать': собирает данные, дешифрует и выводит результат"""
    text = get_input(dec_input)
    if not text:
        messagebox.showerror("Ошибка", "Введите текст для дешифрования.")
        return
    key = validate_key(dec_key)
    if key is None:
        return
    result = caesar_decrypt(text, key)
    if is_error(result):
        messagebox.showerror("Ошибка", result.replace("Ошибка: ", "", 1))
        return
    set_output(dec_output, result)


def on_crack(crack_input, crack_output):
    """Обработчик нажатия кнопки 'Взломать': запускает взлом, выводит текст и показывает окно с найденным ключом"""
    text = get_input(crack_input)
    if not text:
        messagebox.showerror("Ошибка", "Введите зашифрованный текст.")
        return
    key, result = crack_caesar(text)
    if key is None:
        messagebox.showerror("Ошибка", result.replace("Ошибка: ", "", 1))
        return
    set_output(crack_output, result)
    messagebox.showinfo("Взлом выполнен", f"Найденный ключ (сдвиг): {key}")


def build_encrypt_tab(parent):
    """Создает и компонует элементы управления внутри вкладки шифрования."""
    enc_input, enc_key, enc_output = build_text_section(
        parent,
        "Исходный текст:",
        "Зашифрованный текст:",
    )
    ttk.Button(
        parent,
        text="Зашифровать",
        command=lambda: on_encrypt(enc_input, enc_key, enc_output),
    ).pack(anchor="e")


def build_decrypt_tab(parent):
    """Создает и компонует элементы управления внутри вкладки дешифрования."""
    dec_input, dec_key, dec_output = build_text_section(
        parent,
        "Зашифрованный текст:",
        "Расшифрованный текст:",
    )
    ttk.Button(
        parent,
        text="Расшифровать",
        command=lambda: on_decrypt(dec_input, dec_key, dec_output),
    ).pack(anchor="e")


def build_crack_tab(parent):
    """Создает и компонует элементы управления внутри вкладки взлома текста"""
    ttk.Label(
        parent,
        text="Автоматический подбор ключа по частотному анализу (только русский текст).",
        wraplength=480,
    ).pack(anchor="w", pady=(0, 6))
    crack_input, _, crack_output = build_text_section(
        parent,
        "Зашифрованный текст:",
        "Результат взлома:",
        with_key=False,
    )
    ttk.Button(
        parent,
        text="Взломать",
        command=lambda: on_crack(crack_input, crack_output),
    ).pack(anchor="e")


def create_gui(root):
    """Инициализирует главное окно приложения, стили и настраивает вкладки"""
    root.title("Шифр Цезаря")
    root.minsize(620, 520)
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    header = ttk.Label(
        root,
        text="Шифр Цезаря",
        font=("Helvetica", 18, "bold"),
        background="#F0F0F0"
    )
    header.pack(pady=(12, 4))
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=12, pady=8)
    encrypt_frame = ttk.Frame(notebook, padding=8)
    decrypt_frame = ttk.Frame(notebook, padding=8)
    crack_frame = ttk.Frame(notebook, padding=8)
    notebook.add(encrypt_frame, text="Шифрование")
    notebook.add(decrypt_frame, text="Дешифрование")
    notebook.add(crack_frame, text="Взлом (русский)")
    build_encrypt_tab(encrypt_frame)
    build_decrypt_tab(decrypt_frame)
    build_crack_tab(crack_frame)


def main():
    """Точка входа в программу"""
    root = tk.Tk()
    create_gui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
