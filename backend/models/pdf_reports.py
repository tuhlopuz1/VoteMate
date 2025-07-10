import os
import tempfile
from datetime import datetime
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, SimpleDocTemplate, Spacer

# Настройка matplotlib для поддержки кириллицы
matplotlib.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


class PDFReportGenerator:
    def __init__(self, poll_data: dict):
        self.poll_data = poll_data
        self.temp_dir = tempfile.mkdtemp()
        sns.set_theme(style="whitegrid")

    def text_to_image(self, text, font_size=12, width=6 * inch, bg_color=(255, 255, 255, 0)):
        """Конвертирует текст в изображение с прозрачным фоном"""
        # Создаем временное изображение
        fig, ax = plt.subplots(figsize=(width / 100, 1), dpi=100)
        ax.text(0, 0.5, text, fontsize=font_size, fontfamily="DejaVu Sans")
        ax.axis("off")
        fig.patch.set_facecolor(bg_color)

        # Сохраняем в буфер
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi=150, transparent=True)
        plt.close(fig)
        buf.seek(0)

        # Создаем Image object для ReportLab
        return Image(buf, width=width)

    def generate_pdf_report(self) -> str:
        """Генерирует PDF отчет с аналитикой"""
        pdf_path = os.path.join(self.temp_dir, "poll_report.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []

        # Заголовок
        elements.append(self.text_to_image("Аналитический отчет", font_size=20, width=5 * inch))
        elements.append(Spacer(1, 0.2 * inch))

        # Основная информация
        elements.append(self.text_to_image(f"Опрос: {self.poll_data['name']}", font_size=16))
        elements.append(
            self.text_to_image(f"Автор: {self.poll_data.get('user_username', 'Аноним')}")
        )
        elements.append(
            self.text_to_image(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        )
        elements.append(self.text_to_image(f"Всего голосов: {self.poll_data['votes_count']}"))
        elements.append(PageBreak())

        # Результаты
        winner = max(self.poll_data["options"], key=self.poll_data["options"].get)
        winner_votes = self.poll_data["options"][winner]
        winner_percent = (
            winner_votes / self.poll_data["votes_count"] * 100
            if self.poll_data["votes_count"] > 0
            else 0
        )

        elements.append(self.text_to_image("Обзор результатов", font_size=16))
        elements.append(
            self.text_to_image(
                f"Победитель: {winner} с {winner_votes} голосами ({winner_percent:.1f}%)"
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Детальные результаты
        elements.append(self.text_to_image("Детальные результаты", font_size=14))
        for option, votes in self.poll_data["options"].items():
            percent = (
                votes / self.poll_data["votes_count"] * 100
                if self.poll_data["votes_count"] > 0
                else 0
            )
            elements.append(self.text_to_image(f"{option}: {votes} голосов ({percent:.1f}%)"))

        elements.append(PageBreak())

        # Графики
        self._create_bar_chart(elements)
        self._create_pie_chart(elements)
        self._create_boxplot(elements)

        # Собираем документ
        doc.build(elements)
        return pdf_path

    def _create_bar_chart(self, elements):
        """Генерирует bar chart"""
        options = self.poll_data["options"]
        total_votes = self.poll_data["votes_count"]
        if total_votes == 0:
            return

        option_names = list(options.keys())
        votes_values = np.array(list(options.values()))
        percentages = votes_values / total_votes * 100

        plt.figure(figsize=(10, 6))
        sorted_idx = np.argsort(votes_values)[::-1]
        sorted_names = [option_names[i] for i in sorted_idx]
        sorted_pct = percentages[sorted_idx]

        ax = sns.barplot(x=sorted_pct, y=sorted_names, palette="viridis", orient="h")
        ax.set_title("Распределение голосов", fontsize=14)
        ax.set_xlabel("Доля голосов (%)", fontsize=12)
        ax.set_ylabel("")
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        for i, p in enumerate(ax.patches):
            width = p.get_width()
            ax.text(
                width + 0.5,
                p.get_y() + p.get_height() / 2,
                f"{width:.1f}%",
                ha="left",
                va="center",
                fontsize=10,
            )

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        elements.append(self.text_to_image("Распределение голосов", font_size=14))
        elements.append(Image(buf, width=6.5 * inch, height=4 * inch))
        elements.append(Spacer(1, 0.2 * inch))

    def _create_pie_chart(self, elements):
        """Генерирует круговую диаграмму"""
        options = self.poll_data["options"]
        votes_values = np.array(list(options.values()))
        total_votes = sum(votes_values)

        if total_votes == 0:
            return

        plt.figure(figsize=(8, 8))
        threshold = total_votes * 0.03
        labels = [name if value > threshold else "" for name, value in options.items()]
        colors = sns.color_palette("pastel")[0 : len(options)]

        plt.pie(
            votes_values,
            labels=labels,
            autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
            startangle=90,
            counterclock=False,
            colors=colors,
        )
        plt.title("Детальное соотношение голосов", fontsize=14, pad=20)
        plt.axis("equal")

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        elements.append(self.text_to_image("Соотношение голосов", font_size=14))
        elements.append(Image(buf, width=5 * inch, height=5 * inch))
        elements.append(Spacer(1, 0.2 * inch))

    def _create_boxplot(self, elements):
        """Генерирует boxplot"""
        options = self.poll_data["options"]
        if len(options) < 2:
            return

        votes_values = np.array(list(options.values()))

        plt.figure(figsize=(10, 6))
        ax = sns.boxplot(y=votes_values, color="skyblue", width=0.3)
        sns.stripplot(y=votes_values, color="orange", size=8, alpha=0.7, ax=ax)

        plt.title("Распределение голосов по вариантам", fontsize=14)
        plt.ylabel("Количество голосов", fontsize=12)
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        mean_val = np.mean(votes_values)
        plt.axhline(y=mean_val, color="red", linestyle="--", linewidth=1.5)
        plt.text(0.05, mean_val * 1.08, f"Среднее: {mean_val:.1f}", fontsize=10, color="red")

        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        elements.append(self.text_to_image("Анализ распределения", font_size=14))
        elements.append(Image(buf, width=6.5 * inch, height=4 * inch))
        elements.append(Spacer(1, 0.2 * inch))


# Пример использования
if __name__ == "__main__":
    poll_example = {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Лучший язык программирования 2023 года",
        "votes_count": 150,
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_username": "tech_guru",
        "description": "Исследование предпочтений разработчиков в выборе языков программирования",
        "options": {"Python": 65, "JavaScript": 45, "Rust": 25, "Go": 15},
    }

    report_generator = PDFReportGenerator(poll_example)
    report_path = report_generator.generate_pdf_report()
    print(f"PDF отчет сгенерирован: {report_path}")
