"""
Модуль для реализации возможностей экспорта и импорта
"""
import json
import pandas as pd
from data_handlers import DataManager
from mcda_methods import MCDAData


class ExportImportManager:
    """
    Класс для управления возможностями экспорта и импорта
    """
    
    def __init__(self, data_manager: DataManager = None):
        self.data_manager = data_manager
        
    def export_to_pdf(self, analysis_results, filename: str):
        """
        Экспорт результатов анализа в PDF
        """
        # Импортируем здесь, чтобы избежать проблем с зависимостями
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Заголовок отчета
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
            )
            story.append(Paragraph("Отчет по MCDA анализу", title_style))
            
            # Добавляем таблицу с результатами
            if hasattr(analysis_results, 'alternatives'):
                data = [['Альтернатива', 'Рейтинг']]
                for i, rating in enumerate(analysis_results.alternatives):
                    data.append([f'Альтернатива {i+1}', f'{rating:.4f}'])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 12))
            
            doc.build(story)
            print(f"Отчет успешно экспортирован в {filename}")
            
        except ImportError:
            print("Для экспорта в PDF необходимо установить reportlab: pip install reportlab")
    
    def export_to_html(self, analysis_results, filename: str):
        """
        Экспорт результатов анализа в HTML
        """
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Отчет по MCDA анализу</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Отчет по MCDA анализу</h1>
"""
        
        if hasattr(analysis_results, 'alternatives'):
            html_content += "<table><tr><th>Альтернатива</th><th>Рейтинг</th></tr>"
            for i, rating in enumerate(analysis_results.alternatives):
                html_content += f"<tr><td>Альтернатива {i+1}</td><td>{rating:.4f}</td></tr>"
            html_content += "</table>"
        
        html_content += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Отчет успешно экспортирован в {filename}")
    
    def export_analysis_report(self, analysis_data: MCDAData, analysis_results, method_name: str, filename: str):
        """
        Экспорт полного отчета по анализу
        """
        report_data = {
            'method': method_name,
            'criteria_names': analysis_data.criteria_names if hasattr(analysis_data, 'criteria_names') else [],
            'alternatives_names': analysis_data.alternatives_names if hasattr(analysis_data, 'alternatives_names') else [],
            'decision_matrix': analysis_data.matrix.tolist() if hasattr(analysis_data, 'matrix') and hasattr(analysis_data.matrix, 'tolist') else analysis_data.matrix if hasattr(analysis_data, 'matrix') else [],
            'weights': analysis_data.weights.tolist() if hasattr(analysis_data, 'weights') and hasattr(analysis_data.weights, 'tolist') else analysis_data.weights if hasattr(analysis_data, 'weights') else [],
            'results': analysis_results.alternatives.tolist() if hasattr(analysis_results, 'alternatives') and hasattr(analysis_results.alternatives, 'tolist') else analysis_results.alternatives if hasattr(analysis_results, 'alternatives') else []
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"Полный отчет по анализу успешно экспортирован в {filename}")
    
    def import_analysis_template(self, filename: str):
        """
        Импорт шаблона анализа
        """
        with open(filename, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        return template_data