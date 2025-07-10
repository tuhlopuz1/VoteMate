import os
import tempfile
from datetime import datetime
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ======================
# FONT SETUP FOR CYRILLIC
# ======================
try:
    # Try to register Arial font (common on Windows)
    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))
    MAIN_FONT = "Arial"
    BOLD_FONT = "Arial-Bold"
except Exception:
    try:
        # Fallback to DejaVu Sans
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
        MAIN_FONT = "DejaVuSans"
        BOLD_FONT = "DejaVuSans"
    except Exception:
        MAIN_FONT = "Helvetica"
        BOLD_FONT = "Helvetica-Bold"

# Configure matplotlib
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica"]
plt.rcParams["axes.unicode_minus"] = False

# Create stylesheet with registered fonts
styles = getSampleStyleSheet()
# Модифицируем существующие стили вместо добавления новых
styles = getSampleStyleSheet()

# Обновляем стиль 'Title'
styles["Title"].fontName = BOLD_FONT
styles["Title"].fontSize = 24
styles["Title"].leading = 28
styles["Title"].alignment = 1
styles["Title"].spaceAfter = 12
styles["Title"].textColor = colors.HexColor("#2563eb")

# Обновляем стиль 'Heading1'
styles["Heading1"].fontName = BOLD_FONT
styles["Heading1"].fontSize = 18
styles["Heading1"].leading = 22
styles["Heading1"].alignment = 0
styles["Heading1"].spaceBefore = 20
styles["Heading1"].spaceAfter = 10
styles["Heading1"].textColor = colors.HexColor("#0f172a")

# Обновляем стиль 'Heading2'
styles["Heading2"].fontName = BOLD_FONT
styles["Heading2"].fontSize = 16
styles["Heading2"].leading = 20
styles["Heading2"].alignment = 0
styles["Heading2"].spaceBefore = 15
styles["Heading2"].spaceAfter = 8
styles["Heading2"].textColor = colors.HexColor("#2563eb")

# Создаем кастомные стили (если их нет)
if "Body" not in styles:
    styles.add(
        ParagraphStyle(
            name="Body",
            fontName=MAIN_FONT,
            fontSize=12,
            leading=16,
            alignment=0,
            spaceAfter=6,
            textColor=colors.HexColor("#334155"),
        )
    )

if "Caption" not in styles:
    styles.add(
        ParagraphStyle(
            name="Caption",
            fontName=MAIN_FONT,
            fontSize=10,
            leading=12,
            alignment=1,
            spaceBefore=5,
            spaceAfter=15,
            textColor=colors.HexColor("#64748b"),
        )
    )

if "StatValue" not in styles:
    styles.add(
        ParagraphStyle(
            name="StatValue",
            fontName=BOLD_FONT,
            fontSize=14,
            leading=16,
            alignment=1,
            textColor=colors.HexColor("#2563eb"),
        )
    )


# ======================
# REPORT GENERATOR
# ======================
class PremiumPDFReportGenerator:
    def __init__(self, poll_data: dict):
        self.poll_data = poll_data
        self.temp_dir = tempfile.mkdtemp()

    def generate_pdf_report(self) -> str:
        """Generate premium PDF report"""
        poll_id = self.poll_data.get("id", "report")
        pdf_path = os.path.join(self.temp_dir, f"poll_{poll_id}.pdf")

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )
        elements = []

        # Cover page
        self._create_cover_page(elements)
        elements.append(PageBreak())

        # Results overview
        self._create_overview_page(elements)
        elements.append(PageBreak())

        # Detailed results
        self._create_detailed_results(elements)
        elements.append(PageBreak())

        # Visualizations
        self._create_visualizations_page(elements)

        # Build document
        doc.build(elements)
        return pdf_path

    def _create_cover_page(self, elements):
        """Create premium cover page"""
        # Title
        elements.append(Paragraph("АНАЛИТИЧЕСКИЙ ОТЧЕТ", styles["Title"]))
        elements.append(Spacer(1, 1 * cm))

        # Poll title
        elements.append(Paragraph(self.poll_data["name"], styles["Heading1"]))
        elements.append(Spacer(1, 1.5 * cm))

        # Metadata
        elements.append(
            Paragraph(f"Автор: {self.poll_data.get('user_username', 'Аноним')}", styles["Body"])
        )
        elements.append(
            Paragraph(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Body"])
        )
        elements.append(
            Paragraph(f"Всего голосов: {self.poll_data['votes_count']}", styles["Body"])
        )
        elements.append(
            Paragraph(f"Количество вариантов: {len(self.poll_data['options'])}", styles["Body"])
        )

        if self.poll_data.get("description"):
            elements.append(Spacer(1, 1 * cm))
            elements.append(Paragraph("Описание:", styles["Heading2"]))
            elements.append(Paragraph(self.poll_data["description"], styles["Body"]))

        elements.append(Spacer(1, 3 * cm))
        elements.append(Paragraph("Сгенерировано PollAnalytics Pro", styles["Caption"]))

    def _create_overview_page(self, elements):
        """Create results overview page"""
        # Header
        elements.append(Paragraph("ОБЗОР РЕЗУЛЬТАТОВ", styles["Title"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Winner block
        winner = max(self.poll_data["options"], key=self.poll_data["options"].get)
        winner_votes = self.poll_data["options"][winner]
        winner_percent = (
            winner_votes / self.poll_data["votes_count"] * 100
            if self.poll_data["votes_count"] > 0
            else 0
        )

        winner_table = Table(
            [
                [Paragraph("ПОБЕДИТЕЛЬ", styles["Heading2"])],
                [Paragraph(winner, styles["Heading1"])],
                [Paragraph(f"{winner_votes} голосов ({winner_percent:.1f}%)", styles["StatValue"])],
            ],
            colWidths=[15 * cm],
        )

        winner_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eff6ff")),
                    ("BACKGROUND", (0, 2), (-1, 2), colors.white),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2563eb")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("PADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )

        elements.append(winner_table)
        elements.append(Spacer(1, 1 * cm))

        # Results summary
        elements.append(Paragraph("РАСПРЕДЕЛЕНИЕ ГОЛОСОВ", styles["Heading2"]))
        elements.append(Spacer(1, 0.3 * cm))

        # Create summary table
        options = list(self.poll_data["options"].items())
        options.sort(key=lambda x: x[1], reverse=True)

        table_data = []
        for option, votes in options:
            percent = (
                votes / self.poll_data["votes_count"] * 100
                if self.poll_data["votes_count"] > 0
                else 0
            )
            table_data.append([option, str(votes), f"{percent:.1f}%"])

        # Create table
        table = Table(
            [["Вариант", "Голоса", "Доля (%)"], *table_data],
            colWidths=[10 * cm, 2.5 * cm, 2.5 * cm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("FONTNAME", (0, 1), (-1, -1), MAIN_FONT),
                    ("FONTSIZE", (0, 1), (-1, -1), 11),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f0f9ff")],
                    ),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 1 * cm))

        # Add insights
        elements.append(Paragraph("КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ", styles["Heading2"]))
        elements.append(Spacer(1, 0.3 * cm))

        votes = list(self.poll_data["options"].values())
        max_vote = max(votes)
        min_vote = min(votes)
        ratio = max_vote / min_vote if min_vote > 0 else 0

        insights = [
            f"• Победитель получил {winner_percent:.1f}% от общего числа голосов",
            f"• Самый популярный вариант имеет {ratio:.1f}x больше голосов, чем наименее популярный",
            "• Результаты показывают явные предпочтения среди участников",
            "• Распределение указывает на поляризацию мнений",
        ]

        for insight in insights:
            elements.append(Paragraph(insight, styles["Body"]))
            elements.append(Spacer(1, 0.2 * cm))

    def _create_detailed_results(self, elements):
        """Create detailed results page"""
        elements.append(Paragraph("ДЕТАЛЬНЫЙ АНАЛИЗ", styles["Title"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Create statistical cards
        votes = list(self.poll_data["options"].values())
        total = sum(votes)
        mean_val = np.mean(votes) if len(votes) > 0 else 0
        std_val = np.std(votes) if len(votes) > 0 else 0
        gini = self._calculate_gini(votes) if len(votes) > 0 else 0

        stats = [
            ("Всего голосов", total),
            ("Вариантов", len(votes)),
            ("Среднее значение", f"{mean_val:.1f}"),
            ("Стандартное отклонение", f"{std_val:.1f}"),
            ("Коэффициент Джини", f"{gini:.3f}"),
            ("Разброс голосов", f"{min(votes)} - {max(votes)}"),
        ]

        # Create stats grid
        stat_cards = []
        for title, value in stats:
            card = [[Paragraph(title, styles["Body"]), Paragraph(str(value), styles["StatValue"])]]
            stat_cards.append(card)

        # Arrange in 3x2 grid
        grid = Table(
            [
                [Table(stat_cards[0]), Table(stat_cards[1]), Table(stat_cards[2])],
                [Table(stat_cards[3]), Table(stat_cards[4]), Table(stat_cards[5])],
            ],
            colWidths=[5 * cm, 5 * cm, 5 * cm],
        )

        grid.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2563eb")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("PADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )

        elements.append(grid)
        elements.append(Spacer(1, 1 * cm))

        # Detailed distribution
        elements.append(Paragraph("РАСПРЕДЕЛЕНИЕ ПО ВАРИАНТАМ", styles["Heading2"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Create detailed table
        options = list(self.poll_data["options"].items())
        options.sort(key=lambda x: x[1], reverse=True)

        table_data = []
        for i, (option, votes) in enumerate(options):
            percent = votes / total * 100 if total > 0 else 0
            table_data.append([str(i + 1), option, str(votes), f"{percent:.1f}%"])

        detailed_table = Table(
            [["Место", "Вариант", "Голоса", "Доля (%)"], *table_data],
            colWidths=[2 * cm, 9 * cm, 2.5 * cm, 2.5 * cm],
        )

        detailed_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("FONTNAME", (0, 1), (-1, -1), MAIN_FONT),
                    ("FONTSIZE", (0, 1), (-1, -1), 11),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f0f9ff")],
                    ),
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),
                    ("ALIGN", (2, 1), (3, -1), "CENTER"),
                ]
            )
        )

        elements.append(detailed_table)
        elements.append(Spacer(1, 1 * cm))

        # Interpretation
        elements.append(Paragraph("ИНТЕРПРЕТАЦИЯ ДАННЫХ", styles["Heading2"]))
        elements.append(Spacer(1, 0.3 * cm))

        interpretation = [
            "Результаты показывают явные предпочтения участников, с одним вариантом,",
            "доминирующим в опросе. Распределение указывает на поляризацию мнений,",
            "что типично для опросов, основанных на предпочтениях. Победитель получил",
            "значительную поддержку по сравнению с другими вариантами.",
        ]

        for line in interpretation:
            elements.append(Paragraph(line, styles["Body"]))
            elements.append(Spacer(1, 0.1 * cm))

    # def _create_visualizations_page(self, elements):
    #     """Create premium visualizations page"""
    #     elements.append(Paragraph("ВИЗУАЛИЗАЦИЯ ДАННЫХ", styles['Title']))
    #     elements.append(Spacer(1, 0.5*cm))

    #     # Bar chart
    #     self._create_premium_bar_chart(elements)
    #     elements.append(Spacer(1, 1*cm))

    #     # Pie chart
    #     self._create_premium_pie_chart(elements)
    #     elements.append(Spacer(1, 1*cm))

    #     # Box plot
    #     self._create_premium_boxplot(elements)

    #     # Footer
    #     elements.append(Spacer(1, 1*cm))
    #     elements.append(Paragraph(f"Отчет сгенерирован {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Caption']))
    #     elements.append(Paragraph("Конфиденциально - для внутреннего использования", styles['Caption']))

    # В методе _create_visualizations_page заменим вызов боксплота на Парето-диаграмму
    def _create_visualizations_page(self, elements):
        """Create premium visualizations page"""
        elements.append(Paragraph("ВИЗУАЛИЗАЦИЯ ДАННЫХ", styles["Title"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Bar chart
        self._create_premium_bar_chart(elements)
        elements.append(Spacer(1, 1 * cm))

        # Pie chart
        self._create_premium_pie_chart(elements)
        elements.append(Spacer(1, 1 * cm))

        # Pareto chart instead of boxplot
        self._create_premium_boxplot(elements)
        self._create_pareto_chart(elements)

        # Footer
        elements.append(Spacer(1, 1 * cm))
        elements.append(
            Paragraph(
                f"Отчет сгенерирован {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Caption"]
            )
        )
        elements.append(
            Paragraph("Конфиденциально - для внутреннего использования", styles["Caption"])
        )

    # Удалим старый метод _create_premium_boxplot и заменим его на:

    def _create_pareto_chart(self, elements):
        """Create Pareto chart visualization"""
        options = self.poll_data["options"]
        if len(options) < 2:
            return

        # Prepare data
        option_names = list(options.keys())
        votes_values = np.array(list(options.values()))
        total_votes = sum(votes_values)

        if total_votes == 0:
            return

        # Sort descending
        sorted_idx = np.argsort(votes_values)[::-1]
        sorted_names = [option_names[i] for i in sorted_idx]
        sorted_votes = votes_values[sorted_idx]
        percentages = sorted_votes / total_votes * 100

        # Calculate cumulative percentage
        cumulative_percent = np.cumsum(percentages)

        # Create figure
        plt.figure(figsize=(12, 6), dpi=120)
        ax1 = plt.gca()

        # Create bars
        bars = ax1.bar(sorted_names, percentages, color="#60a5fa", alpha=0.7)
        ax1.set_xlabel("Варианты ответа")
        ax1.set_ylabel("Доля голосов (%)", color="#2563eb")
        ax1.tick_params(axis="y", labelcolor="#2563eb")

        # Create cumulative line
        ax2 = ax1.twinx()
        ax2.plot(
            sorted_names,
            cumulative_percent,
            color="#ef4444",
            marker="o",
            linestyle="-",
            linewidth=2,
            markersize=6,
        )
        ax2.set_ylabel("Накопленный процент (%)", color="#ef4444")
        ax2.tick_params(axis="y", labelcolor="#ef4444")
        ax2.grid(visible=False)

        # Set titles and labels
        plt.title("Диаграмма Парето: распределение голосов", fontsize=14, pad=15)
        plt.xticks(rotation=45, ha="right")

        # Add value labels
        for bar, percent in zip(bars, percentages):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{percent:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#1e3a8a",
            )

        for i, cum_pct in enumerate(cumulative_percent):
            ax2.text(
                i,
                cum_pct + 2,
                f"{cum_pct:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#b91c1c",
                fontweight="bold",
            )

        plt.tight_layout()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        # Add to elements
        elements.append(Paragraph("Анализ по принципу Парето", styles["Heading2"]))
        elements.append(Image(buf, width=16 * cm, height=8 * cm))

    def _create_premium_bar_chart(self, elements):
        """Create premium bar chart visualization"""
        options = self.poll_data["options"]
        total_votes = self.poll_data["votes_count"]
        if total_votes == 0:
            return

        option_names = list(options.keys())
        votes_values = np.array(list(options.values()))
        percentages = votes_values / total_votes * 100

        # Sort data
        sorted_idx = np.argsort(votes_values)[::-1]
        sorted_names = [option_names[i] for i in sorted_idx]
        sorted_pct = percentages[sorted_idx]

        # Create figure with modern style
        plt.figure(figsize=(12, 6), dpi=120)
        ax = plt.subplot()

        # Create gradient bars
        colors = plt.cm.Blues(np.linspace(0.4, 1, len(sorted_names)))
        for i, (name, pct) in enumerate(zip(sorted_names, sorted_pct)):
            ax.barh(name, pct, height=0.7, color=colors[i], edgecolor="white", linewidth=1.5)

            # Add value inside bar
            ax.text(
                pct - 3,
                i,
                f"{pct:.1f}%",
                ha="right",
                va="center",
                color="white",
                fontweight="bold",
                fontsize=10,
            )

        # Styling
        ax.set_title("Распределение голосов", fontsize=14, pad=15)
        ax.set_xlabel("Доля голосов (%)", fontsize=12, labelpad=10)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        plt.tight_layout()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        # Add to elements
        elements.append(Paragraph("Анализ распределения голосов", styles["Heading2"]))
        elements.append(Image(buf, width=16 * cm, height=8 * cm))

    def _create_premium_pie_chart(self, elements):
        """Create premium pie chart visualization"""
        options = self.poll_data["options"]
        votes_values = np.array(list(options.values()))
        total_votes = sum(votes_values)

        if total_votes == 0:
            return

        # Prepare data
        labels = options.keys()
        sizes = votes_values
        explode = [0.05 if size < 0.1 * total_votes else 0 for size in sizes]

        # Create figure
        plt.figure(figsize=(8, 8), dpi=120)
        ax = plt.subplot()

        # Create pie chart with effects
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False,
            explode=explode,
            colors=plt.cm.Pastel1.colors,
            shadow=True,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 10},
        )

        # Style percentages
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")

        # Equal aspect ratio
        ax.axis("equal")
        ax.set_title("Соотношение голосов", fontsize=14, pad=20)

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        # Add to elements
        elements.append(Paragraph("Анализ соотношения голосов", styles["Heading2"]))
        elements.append(Image(buf, width=12 * cm, height=12 * cm))

    def _create_premium_boxplot(self, elements):
        """Create premium boxplot visualization"""
        options = self.poll_data["options"]
        if len(options) < 2:
            return

        votes_values = np.array(list(options.values()))

        # Create figure
        plt.figure(figsize=(10, 6), dpi=120)
        ax = plt.subplot()

        # Create boxplot with modern style
        box = ax.boxplot(
            votes_values,
            vert=False,
            patch_artist=True,
            widths=0.6,
            showmeans=True,
            meanprops={
                "marker": "D",
                "markerfacecolor": "orange",
                "markeredgecolor": "white",
                "markersize": 8,
            },
        )

        # Style boxes
        for patch in box["boxes"]:
            patch.set_facecolor("#60a5fa")
            patch.set_alpha(0.7)

        # Add data points
        ax.scatter(
            votes_values,
            [1] * len(votes_values),
            color="orange",
            s=80,
            alpha=0.7,
            edgecolor="white",
            linewidth=1,
        )

        # Add mean line
        mean_val = np.mean(votes_values)
        ax.axvline(mean_val, color="red", linestyle="--", linewidth=2)
        ax.text(mean_val + 0.5, 1.2, f"Среднее: {mean_val:.1f}", color="red", fontweight="bold")

        # Styling
        ax.set_title("Статистическое распределение", fontsize=14, pad=15)
        ax.set_xlabel("Количество голосов", fontsize=12, labelpad=10)
        ax.set_yticklabels([])
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        plt.tight_layout()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close()
        buf.seek(0)

        # Add to elements
        elements.append(Paragraph("Анализ статистического распределения", styles["Heading2"]))
        elements.append(Image(buf, width=14 * cm, height=6 * cm))

    def _calculate_gini(self, votes):
        """Calculate Gini coefficient for vote distribution"""
        if len(votes) == 0 or sum(votes) == 0:
            return 0
        votes_sorted = np.sort(votes)
        n = len(votes_sorted)
        cum_votes = np.cumsum(votes_sorted)
        return 1 - 2 * np.sum(cum_votes) / (n * cum_votes[-1]) + 1 / n


# # Example usage
# if __name__ == "__main__":
#     poll_example = {
#         "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
#         "name": "Лучший язык программирования 2023 года",
#         "votes_count": 150,
#         "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
#         "user_username": "tech_guru",
#         "description": "Исследование предпочтений разработчиков в выборе языков программирования для новых проектов в 2023 году",
#         "options": {
#             "Python": 65,
#             "JavaScript": 45,
#             "Rust": 25,
#             "Go": 15
#         }
#     }

#     report_generator = PremiumPDFReportGenerator(poll_example)
#     report_path = report_generator.generate_pdf_report()
#     print(f"Premium PDF report generated: {report_path}")
