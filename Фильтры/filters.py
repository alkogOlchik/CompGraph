import sys
import importlib.resources
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QScrollArea, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageLoaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Filters")
        self.setGeometry(300, 300, 900, 600)
        self.setStyleSheet('background-color: #29272E;')

        # Основной виджет
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Основной макет (горизонтальный)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Левая часть: изображение и кнопки загрузки, сохранения, сброса
        left_layout = QVBoxLayout()

        # Метка для отображения изображения
        self.image_label = QLabel("Изображение не загружено", self)
        self.image_label.setStyleSheet("border-radius: 5px; background-color: #54505E;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(500, 450)
        left_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Кнопки загрузки, сохранения и сброса
        buttons_layout = QHBoxLayout()

        self.load_button = QPushButton("Загрузить изображение", self)
        self.load_button.setFixedSize(200, 60)
        self.load_button.setStyleSheet('''
            QPushButton {
                background-color: #5109B6;
                border-radius: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6A1DB6;
            }
            QPushButton:pressed {
                background-color: #400C8D;
            }
        ''')
        self.load_button.clicked.connect(self.load_image)
        buttons_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Сохранить изображение", self)
        self.save_button.setFixedSize(200, 60)
        self.save_button.setStyleSheet('''
            QPushButton {
                background-color: #5109B6;
                border-radius: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6A1DB6;
            }
            QPushButton:pressed {
                background-color: #400C8D;
            }
        ''')
        self.save_button.clicked.connect(self.save_image)
        buttons_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Сбросить фильтры", self)
        self.reset_button.setFixedSize(200, 60)
        self.reset_button.setStyleSheet('''
            QPushButton {
                background-color: #5109B6;
                border-radius: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6A1DB6;
            }
            QPushButton:pressed {
                background-color: #400C8D;
            }
        ''')
        self.reset_button.clicked.connect(self.reset_filters)
        buttons_layout.addWidget(self.reset_button)

        left_layout.addLayout(buttons_layout)

        self.main_layout.addLayout(left_layout)

        # Правая часть: Scroll Area с кнопками фильтров
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(550, 25, 250, 500)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #54505E;
                border-radius: 10px;
                border: 2px solid #333;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #B0B0B0;
                border-radius: 4px;
                min-height: 5px;
            }
            QScrollBar::groove{
                background: transparent;
            }
            QScrollBar::handle:vertical:hover {
                background: #C0C0C0;
            }
            QScrollBar::handle:vertical:pressed {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
                height: 0px;
                width: 0px;
            }
        """)
        self.scroll_area.setWidgetResizable(True)

        # Контейнер для кнопок фильтров внутри Scroll Area
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setSpacing(10)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_area.setWidget(self.container_widget)

        # Стиль для кнопок фильтров
        button_style = '''
            QPushButton {
                background-color: #5109B6;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #6A1DB6;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background-color: #400C8D;
            }
        '''

        # Список фильтров
        self.filter_buttons = [
            ("Черно-белый", self.apply_grayscale),
            ("Инверсия", self.apply_invert_colors),
            ("Рыбий глаз", self.apply_fish_eye),
            ("Плывет", self.apply_chromatic_aberration),
            ("Блюр", self.apply_blur),
            ("Контраст", self.apply_increase_contrast),
            ("Пиксели", self.apply_pixelation),
            ("Сепия", self.apply_sepia),
            ("Резкость", self.apply_sharpness),
            ("Глитч", self.apply_glitch),
            ("Рельеф", self.apply_emboss)
        ]

        # Добавление кнопок фильтров в контейнер
        for name, func in self.filter_buttons:
            button = QPushButton(name, self)
            button.setFixedHeight(50)
            button.setStyleSheet(button_style)
            button.clicked.connect(func)
            self.container_layout.addWidget(button)

        self.container_layout.addStretch()  # Добавляет растяжение в конец макета

        self.main_layout.addWidget(self.scroll_area)

        # Хранение изображений
        self.original_image = None
        self.current_image = None

    def load_image(self):
        """Загрузка изображения."""
        image_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if image_path:
            self.original_image = Image.open(image_path).convert("RGB")
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)

    def save_image(self):
        """Сохранение текущего изображения."""
        if self.current_image:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
            )
            if save_path:
                self.current_image.save(save_path)
        else:
            print("No image to save")

    def reset_filters(self):
        """Сброс фильтров до оригинального изображения."""
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)

    def display_image(self, image):
        """Отображение изображения в интерфейсе."""
        qimage = QImage(
            image.tobytes(),
            image.width,
            image.height,
            image.width * 3,
            QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # Фильтры
    def apply_grayscale(self):
        if self.current_image:
            np_image = np.array(self.current_image)
            gray_image = np.dot(np_image[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            self.current_image = Image.fromarray(gray_image, mode="L").convert("RGB")
            self.display_image(self.current_image)

    def apply_invert_colors(self):
        if self.current_image:
            np_image = np.array(self.current_image)
            inverted_image = 255 - np_image
            self.current_image = Image.fromarray(inverted_image)
            self.display_image(self.current_image)

    def apply_fish_eye(self):
        if self.current_image:
            np_image = np.array(self.current_image)
            h, w, _ = np_image.shape
            y, x = np.indices((h, w))
            x_center, y_center = w / 2, h / 2
            x_new = x - x_center
            y_new = y - y_center
            r = np.sqrt(x_new**2 + y_new**2)
            r_max = np.max(r)
            # Логарифмическое искажение
            x_new = x_center + x_new * np.log(r + 1) / np.log(r_max + 1)
            y_new = y_center + y_new * np.log(r + 1) / np.log(r_max + 1)
            coords = np.stack([y_new.ravel(), x_new.ravel()], axis=-1).round().astype(int)
            coords = np.clip(coords, 0, [h - 1, w - 1])
            fish_eye_image = np_image[coords[:, 0], coords[:, 1]].reshape((h, w, -1))
            self.current_image = Image.fromarray(fish_eye_image)
            self.display_image(self.current_image)

    def apply_chromatic_aberration(self):
        """Эффект смешанного искажения."""
        if self.current_image:
            # Преобразуем изображение в массив NumPy
            np_image = np.array(self.current_image)
            h, w, c = np_image.shape

            # Создаем сетку координат
            y, x = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")

            # Создаем случайные искажения
            distortion_x = np.sin(y / 20) * 10  # Волновое искажение по оси X
            distortion_y = np.cos(x / 20) * 10  # Волновое искажение по оси Y



            # Применяем искажения к координатам
            new_x = np.clip(x + distortion_x.astype(np.int32), 0, w - 1)
            new_y = np.clip(y + distortion_y.astype(np.int32), 0, h - 1)

            # Перемешиваем пиксели изображения
            distorted_image = np_image[new_y, new_x]

            # Преобразуем результат обратно в изображение
            self.current_image = Image.fromarray(distorted_image)
            self.display_image(self.current_image)

    def apply_blur(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(5))
            self.display_image(self.current_image)

    def apply_sepia(self):
        if self.current_image:
            np_image = np.array(self.current_image)
            tr = 0.393 * np_image[..., 0] + 0.769 * np_image[..., 1] + 0.189 * np_image[..., 2]
            tg = 0.349 * np_image[..., 0] + 0.686 * np_image[..., 1] + 0.168 * np_image[..., 2]
            tb = 0.272 * np_image[..., 0] + 0.534 * np_image[..., 1] + 0.131 * np_image[..., 2]
            np_image[..., 0] = np.clip(tr, 0, 255)
            np_image[..., 1] = np.clip(tg, 0, 255)
            np_image[..., 2] = np.clip(tb, 0, 255)
            self.current_image = Image.fromarray(np_image)
            self.display_image(self.current_image)

    def apply_increase_contrast(self):
        if self.current_image:
            enhancer = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer.enhance(2.0)
            self.display_image(self.current_image)

    def apply_pixelation(self, pixel_size=10):
        """Применение фильтра пикселизации."""
        if self.original_image:
            np_image = np.array(self.original_image)
            h, w, _ = np_image.shape

            # Проверка, чтобы размер пикселей не превышал размеры изображения
            pixel_size = 10

            # Уменьшаем изображение, создавая эффект пикселизации
            small_h, small_w = h // pixel_size, w // pixel_size
            small_image = np_image[:small_h * pixel_size, :small_w * pixel_size]
            small_image = small_image.reshape(small_h, pixel_size, small_w, pixel_size, 3).mean(axis=(1, 3)).astype(
                np.uint8)

            # Увеличиваем изображение обратно
            pixelated_image = np.kron(small_image, np.ones((pixel_size, pixel_size, 1), dtype=np.uint8))

            # Создаем новое изображение
            self.current_image = Image.fromarray(pixelated_image[:h, :w, :])
            self.display_image(self.current_image)

    def apply_sharpness(self):
        if self.current_image:
            enhancer = ImageEnhance.Sharpness(self.current_image)
            self.current_image = enhancer.enhance(10.0)
            self.display_image(self.current_image)

    def apply_emboss(self):
        """Рельефный эффект."""
        if self.current_image:
            try:
                np_image = np.array(self.current_image, dtype=np.float32)
                kernel = np.array([[0, -4, 0],
                                   [-1, 7, -1],
                                   [0, -1, 0]])

                # Применяем фильтр свертки для рельефа
                from scipy.signal import convolve2d
                gray_image = np.dot(np_image[..., :3], [0.299, 0.587, 0.114])
                embossed_image = convolve2d(gray_image, kernel, mode='same', boundary='wrap')
                embossed_image = np.clip(embossed_image + 128, 0, 255).astype(np.uint8)
                self.current_image = Image.fromarray(embossed_image, mode="L").convert("RGB")
                self.display_image(self.current_image)
            except Exception as e:
                print(f"Ошибка при применении рельефа: {e}")

    def apply_glitch(self):
        """Глич-эффект с разрезами и сдвигами."""
        if self.current_image:
            # Преобразуем изображение в массив NumPy
            np_image = np.array(self.current_image)
            h, w, _ = np_image.shape

            # Сдвигаем цветовые каналы
            r_shift = np.roll(np_image[..., 0], shift=10, axis=1)
            g_shift = np.roll(np_image[..., 1], shift=-10, axis=0)
            b_shift = np.roll(np_image[..., 2], shift=5, axis=1)

            # Собираем каналы с искажениями
            glitched_image = np.stack([r_shift, g_shift, b_shift], axis=-1)

            # Разрезаем изображение на полосы
            num_slices = 10  # Количество разрезов
            slice_height = h // num_slices  # Высота одной полосы

            for i in range(num_slices):
                # Вычисляем координаты текущей полосы
                y_start = i * slice_height
                y_end = (i + 1) * slice_height if i != num_slices - 1 else h

                # Сдвиг полосы на случайное значение влево или вправо
                shift = np.random.randint(-20, 20)
                glitched_image[y_start:y_end] = np.roll(glitched_image[y_start:y_end], shift=shift, axis=1)

            # Конвертируем обратно в изображение и отображаем
            self.current_image = Image.fromarray(glitched_image)
            self.display_image(self.current_image)

    def apply_vintage(self):
        """Старинный стиль."""
        if self.current_image:
            np_image = np.array(self.current_image)
            vintage_filter = np.array([0.9, 0.7, 0.4])
            np_image = np.clip(np_image * vintage_filter, 0, 255)
            self.current_image = Image.fromarray(np_image.astype(np.uint8))
            self.display_image(self.current_image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ImageLoaderApp()
    main_window.show()
    sys.exit(app.exec_())


