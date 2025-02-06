import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import math


class ImageReflectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mirror")
        self.root.configure(bg="#29272E")
        self.root.geometry("1920x1080")  # Фиксированный размер окна

        self.image = None
        self.processed_image = None
        self.reflection_angle = 0
        self.reflection_offset = 0
        self.color_criterion = "all"  # "all", "black", "white", "red", "green", "blue"

        # Интерфейс
        self.setup_ui()

    def setup_ui(self):
        # Основной фрейм для центрирования
        frame_main = tk.Frame(self.root, bg="#29272E")
        frame_main.pack(fill="both", expand=True, padx=20, pady=20)

        # Фрейм для кнопок и ползунков
        frame_controls = tk.Frame(frame_main, bg="#29272E", width=250)
        frame_controls.pack(side="left", fill="y", padx=10)

        # Кнопка загрузки
        self.load_button = tk.Button(
            frame_controls, text="Загрузить картинку", bg="#4B0082", fg="white",
            font=("Arial", 12, "bold"), command=self.load_image
        )
        self.load_button.pack(fill="x", pady=10)

        # Кнопка обработки
        self.process_button = tk.Button(
            frame_controls, text="Обработать", bg="#4B0082", fg="white",
            font=("Arial", 12, "bold"), command=self.apply_reflection
        )
        self.process_button.pack(fill="x", pady=10)

        # Фрейм для ползунков и меню
        frame_sliders = tk.Frame(frame_controls, bg="#1E1E2F")
        frame_sliders.pack(fill="x", pady=10)

        # Ползунок угла
        tk.Label(frame_sliders, text="Угол отражения (°):", bg="#1E1E2F", fg="white",
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.angle_slider = tk.Scale(
            frame_sliders, from_=0, to=360, orient="horizontal", bg="#4B0082", fg="white",
            troughcolor="#2C2C3E", highlightthickness=0, command=self.update_reflection
        )
        self.angle_slider.set(0)
        self.angle_slider.pack(fill="x", padx=10)

        # Ползунок смещения
        tk.Label(frame_sliders, text="Смещение линии:", bg="#1E1E2F", fg="white",
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.offset_slider = tk.Scale(
            frame_sliders, from_=-200, to=200, orient="horizontal", bg="#4B0082", fg="white",
            troughcolor="#2C2C3E", highlightthickness=0, command=self.update_reflection
        )
        self.offset_slider.set(0)
        self.offset_slider.pack(fill="x", padx=10)

        # Выбор критерия отображения
        tk.Label(frame_sliders, text="Признак отражения:", bg="#1E1E2F", fg="white",
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.criterion_menu = tk.OptionMenu(
            frame_sliders, tk.StringVar(value="Все цвета"), "Все цвета", "Черный", "Белый", "Красный", "Зеленый", "Синий", command=self.set_criterion
        )
        self.criterion_menu.config(bg="#4B0082", fg="white", font=("Arial", 12, "bold"))
        self.criterion_menu.pack(fill="x", padx=10)

        # Фрейм для изображения и прокрутки
        frame_canvas = tk.Frame(frame_main, bg="#1E1E2F")
        frame_canvas.pack(side="right", fill="both", expand=True, padx=10)

        # Создаем полосу прокрутки
        self.canvas_scrollbar = tk.Scrollbar(frame_canvas, orient="vertical")
        self.canvas_scrollbar.pack(side="right", fill="y")

        # Создаем Canvas для отображения изображения
        self.image_canvas = tk.Canvas(frame_canvas, bg="gray", yscrollcommand=self.canvas_scrollbar.set)
        self.image_canvas.pack(side="left", fill="both", expand=True)

        # Подключаем полосу прокрутки к Canvas
        self.canvas_scrollbar.config(command=self.image_canvas.yview)

    def load_image(self):
        """Загрузка изображения."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path:
            return

        self.image = Image.open(file_path).convert("RGBA")
        self.processed_image = self.image.copy()
        self.display_image(self.processed_image)
        self.update_reflection()

    def apply_reflection(self):
        """Обработка изображения с отражением."""
        if not self.image:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение!")
            return

        reflected_image = self.reflect_image()
        self.processed_image = reflected_image
        self.display_image(reflected_image)

    def reflect_image(self):
        """Функция для создания отражения изображения."""
        img = self.image.copy()
        angle_rad = math.radians(self.reflection_angle)
        center_x = img.width // 2 + self.reflection_offset
        center_y = img.height // 2

        pixels = img.load()
        width, height = img.size

        # Итерация по пикселям и создание отражения
        for y in range(height):
            for x in range(width):
                original_color = pixels[x, y]
                # Проверка критерия цвета
                if not self.check_color(original_color):
                    continue

                # Определяем расстояние до линии
                rx, ry = x - center_x, y - center_y
                distance = rx * math.cos(angle_rad) + ry * math.sin(angle_rad)

                # Вычисляем отражённые координаты
                ref_x = int(x - 2 * distance * math.cos(angle_rad))
                ref_y = int(y - 2 * distance * math.sin(angle_rad))

                # Если координаты в пределах изображения
                if 0 <= ref_x < width and 0 <= ref_y < height:
                    if distance > 0:  # Отражение происходит только на одной стороне линии
                        pixels[x, y] = img.getpixel((ref_x, ref_y))

        # Рисуем перпендикулярную линию на изображении
        draw = ImageDraw.Draw(img)
        line_length = max(width, height)

        # Вычисляем перпендикуляр к линии отражения
        perp_angle_rad = angle_rad + math.pi / 2
        x1 = center_x - line_length * math.cos(perp_angle_rad)
        y1 = center_y - line_length * math.sin(perp_angle_rad)
        x2 = center_x + line_length * math.cos(perp_angle_rad)
        y2 = center_y + line_length * math.sin(perp_angle_rad)

        draw.line([(x1, y1), (x2, y2)], fill="red", width=3)

        return img

    def check_color(self, color):
        """Проверяет, соответствует ли цвет критерию."""
        r, g, b, a = color  # RGBA
        if self.color_criterion == "Черный":
            return r < 50 and g < 50 and b < 50  # Очень темные цвета
        elif self.color_criterion == "Белый":
            return r > 200 and g > 200 and b > 200  # Очень светлые цвета
        elif self.color_criterion == "Красный":
            return r > g and r > b  # Красные пиксели
        elif self.color_criterion == "Зеленый":
            return g > r and g > b  # Зеленые пиксели
        elif self.color_criterion == "Синий":
            return b > r and b > g  # Синие пиксели
        return True  # Если критерий - все цвета ("all")

    def set_criterion(self, value):
        """Устанавливает критерий отображения."""
        self.color_criterion = value
        self.update_reflection()

    def update_reflection(self, _=None):
        """Обновление линии в реальном времени."""
        if not self.image:
            return

        # Обновляем угол и смещение
        self.reflection_angle = self.angle_slider.get()
        self.reflection_offset = self.offset_slider.get()

        # Рисуем перпендикулярную линию
        img = self.image.copy()
        draw = ImageDraw.Draw(img)
        angle_rad = math.radians(self.reflection_angle)
        center_x = img.width // 2 + self.reflection_offset
        center_y = img.height // 2
        line_length = max(img.width, img.height)

        # Перпендикулярная линия
        perp_angle_rad = angle_rad + math.pi / 2
        x1 = center_x - line_length * math.cos(perp_angle_rad)
        y1 = center_y - line_length * math.sin(perp_angle_rad)
        x2 = center_x + line_length * math.cos(perp_angle_rad)
        y2 = center_y + line_length * math.sin(perp_angle_rad)
        draw.line([(x1, y1), (x2, y2)], fill="red", width=3)

        self.display_image(img)

    def display_image(self, img):
        """Отображение изображения на Canvas."""
        img_width, img_height = img.size

        # Устанавливаем размер canvas, если изображение больше
        self.image_canvas.config(scrollregion=(0, 0, img_width, img_height))

        img_tk = ImageTk.PhotoImage(img)
        self.image_canvas.create_image(0, 0, anchor="nw", image=img_tk)
        self.image_canvas.image = img_tk  # Сохраняем ссылку на изображение


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageReflectionApp(root)
    root.mainloop()
