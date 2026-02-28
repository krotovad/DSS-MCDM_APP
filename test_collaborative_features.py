"""
Тестовый файл для проверки работы коллаборативных функций
"""
import os
import sys
sys.path.insert(0, '/workspace')

from collaborative_features import ProjectManager, CommentSystem, VersionControl


def test_project_management():
    """Тестирует основные функции управления проектами"""
    print("=== Тестирование управления проектами ===")
    
    # Создаем менеджер проектов
    pm = ProjectManager("./test_projects")
    
    # Создаем проект
    pm.create_project("test_project", "Тестовый проект для проверки функций")
    
    # Открываем проект
    pm.open_project("test_project")
    
    # Создаем фиктивные данные анализа для тестирования
    class MockAnalysisData:
        def __init__(self):
            self.criteria = ["crit1", "crit2"]
            self.alternatives = ["alt1", "alt2"]
            self.matrix = [[1, 2], [3, 4]]
            self.weights = [0.5, 0.5]
    
    mock_data = MockAnalysisData()
    
    # Сохраняем состояние проекта
    pm.save_project_state(mock_data, "TOPSIS", "initial_state")
    
    # Загружаем состояние проекта
    loaded_state = pm.load_project_state("initial_state")
    print(f"Загруженное состояние: {loaded_state['method']}")


def test_comment_system():
    """Тестирует систему комментариев"""
    print("\n=== Тестирование системы комментариев ===")
    
    # Создаем менеджер проектов
    pm = ProjectManager("./test_projects")
    pm.open_project("test_project")
    
    # Создаем систему комментариев
    cs = CommentSystem(pm)
    
    # Добавляем комментарии
    cs.add_comment("analysis_1", "Первый результат выглядит многообещающе", "Аналитик 1")
    cs.add_comment("analysis_1", "Согласен, но стоит рассмотреть также веса критериев", "Аналитик 2")
    cs.add_comment("analysis_2", "Второй анализ требует дополнительной проверки", "Руководитель")
    
    # Получаем комментарии
    comments = cs.get_comments("analysis_1")
    print(f"Количество комментариев для анализа 1: {len(comments)}")
    for comment in comments:
        print(f"  - {comment['author']}: {comment['comment']}")


def test_version_control():
    """Тестирует систему версионирования"""
    print("\n=== Тестирование системы версионирования ===")
    
    # Создаем менеджер проектов
    pm = ProjectManager("./test_projects")
    pm.open_project("test_project")
    
    # Создаем систему контроля версий
    vc = VersionControl(pm)
    
    # Создаем фиктивные данные модели для тестирования
    class MockModelData:
        def __init__(self):
            self.method = "TOPSIS"
            self.parameters = {"normalize": True, "weights": [0.4, 0.6]}
            self.results = {"alternative_1": 0.75, "alternative_2": 0.62}
    
    mock_model = MockModelData()
    
    # Создаем несколько версий модели
    vc.create_version(mock_model, "Начальная версия модели")
    vc.create_version(mock_model, "Добавлены новые критерии", "1.1.0")
    vc.create_version(mock_model, "Оптимизированы веса", "1.1.1")
    
    # Получаем историю версий
    history = vc.get_version_history()
    print(f"Количество версий: {len(history)}")
    for version in history:
        print(f"  - {version['version']}: {version['description']}")
    
    # Загружаем версию
    loaded_version = vc.load_version("1.1.0")
    print(f"Загруженная версия 1.1.0 использует метод: {loaded_version['method']}")


if __name__ == "__main__":
    test_project_management()
    test_comment_system()
    test_version_control()
    
    print("\n=== Все тесты пройдены успешно ===")