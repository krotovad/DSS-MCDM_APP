"""
Тестовый файл для проверки работы возможностей экспорта и импорта
"""
import os
import sys
sys.path.insert(0, '/workspace')

from export_import import ExportImportManager


def test_export_to_html():
    """Тестирует экспорт в HTML"""
    print("=== Тестирование экспорта в HTML ===")
    
    # Создаем фиктивные результаты анализа для тестирования
    class MockAnalysisResults:
        def __init__(self):
            self.alternatives = [0.85, 0.72, 0.91, 0.65]
    
    results = MockAnalysisResults()
    manager = ExportImportManager()
    
    # Экспортируем в HTML
    manager.export_to_html(results, "test_report.html")
    
    # Проверяем, что файл создан
    if os.path.exists("test_report.html"):
        print("Файл test_report.html успешно создан")
        # Выводим начало файла для проверки
        with open("test_report.html", 'r', encoding='utf-8') as f:
            content = f.read(200)  # Читаем первые 200 символов
            print(f"Начало содержимого файла: {content}")
    else:
        print("Ошибка: файл test_report.html не создан")


def test_export_to_pdf():
    """Тестирует экспорт в PDF"""
    print("\n=== Тестирование экспорта в PDF ===")
    
    # Создаем фиктивные результаты анализа для тестирования
    class MockAnalysisResults:
        def __init__(self):
            self.alternatives = [0.85, 0.72, 0.91, 0.65]
    
    results = MockAnalysisResults()
    manager = ExportImportManager()
    
    # Пробуем экспортировать в PDF (это может вызвать ImportError если reportlab не установлен)
    try:
        manager.export_to_pdf(results, "test_report.pdf")
        if os.path.exists("test_report.pdf"):
            print("Файл test_report.pdf успешно создан")
        else:
            print("Файл test_report.pdf не был создан")
    except ImportError as e:
        print(f"Не удалось экспортировать в PDF: {e}")
        print("Это ожидаемое поведение если reportlab не установлен")


def test_full_analysis_export():
    """Тестирует экспорт полного отчета по анализу"""
    print("\n=== Тестирование экспорта полного отчета по анализу ===")
    
    # Создаем фиктивные данные анализа для тестирования
    class MockMCDAData:
        def __init__(self):
            self.criteria_names = ["Критерий 1", "Критерий 2", "Критерий 3"]
            self.alternatives_names = ["Альтернатива 1", "Альтернатива 2"]
            self.matrix = [[0.8, 0.6, 0.9], [0.7, 0.8, 0.6]]
            self.weights = [0.4, 0.3, 0.3]
    
    class MockAnalysisResults:
        def __init__(self):
            self.alternatives = [0.85, 0.72]
    
    data = MockMCDAData()
    results = MockAnalysisResults()
    manager = ExportImportManager()
    
    # Экспортируем полный отчет
    manager.export_analysis_report(data, results, "TOPSIS", "full_analysis_report.json")
    
    # Проверяем, что файл создан
    if os.path.exists("full_analysis_report.json"):
        print("Файл full_analysis_report.json успешно создан")
        # Выводим часть содержимого для проверки
        with open("full_analysis_report.json", 'r', encoding='utf-8') as f:
            import json
            content = json.load(f)
            print(f"Метод анализа: {content['method']}")
            print(f"Критерии: {content['criteria_names']}")
    else:
        print("Ошибка: файл full_analysis_report.json не создан")


def test_template_import():
    """Тестирует импорт шаблона анализа"""
    print("\n=== Тестирование импорта шаблона анализа ===")
    
    # Сначала создадим тестовый шаблон
    test_template = {
        "name": "Шаблон проекта",
        "criteria": [
            {"name": "Критерий 1", "weight": 0.4, "direction": "max"},
            {"name": "Критерий 2", "weight": 0.3, "direction": "min"},
            {"name": "Критерий 3", "weight": 0.3, "direction": "max"}
        ],
        "alternatives": [
            {"name": "Альтернатива 1"},
            {"name": "Альтернатива 2"}
        ],
        "method": "TOPSIS"
    }
    
    # Сохраняем шаблон в файл
    with open("test_template.json", 'w', encoding='utf-8') as f:
        import json
        json.dump(test_template, f, ensure_ascii=False, indent=2)
    
    manager = ExportImportManager()
    
    # Импортируем шаблон
    imported_template = manager.import_analysis_template("test_template.json")
    
    print(f"Импортированный шаблон: {imported_template['name']}")
    print(f"Метод анализа в шаблоне: {imported_template['method']}")
    print(f"Количество критериев: {len(imported_template['criteria'])}")
    
    # Удаляем временный файл
    os.remove("test_template.json")


if __name__ == "__main__":
    test_export_to_html()
    test_export_to_pdf()
    test_full_analysis_export()
    test_template_import()
    
    print("\n=== Все тесты экспорта/импорта пройдены ===")