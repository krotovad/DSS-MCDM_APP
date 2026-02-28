"""
Модуль для реализации коллаборативных функций
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ProjectManager:
    """
    Класс для управления совместной работой над проектами
    """
    
    def __init__(self, project_path: str = "./projects"):
        self.project_path = project_path
        self.current_project = None
        self.ensure_project_directory()
    
    def ensure_project_directory(self):
        """Создает директорию для проектов если она не существует"""
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)
    
    def create_project(self, project_name: str, description: str = ""):
        """Создает новый проект"""
        project_dir = os.path.join(self.project_path, project_name)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        # Создаем файл метаданных проекта
        metadata = {
            "name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "members": [],
            "version": "1.0"
        }
        
        metadata_path = os.path.join(project_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        self.current_project = project_name
        print(f"Проект '{project_name}' успешно создан")
    
    def open_project(self, project_name: str):
        """Открывает существующий проект"""
        project_dir = os.path.join(self.project_path, project_name)
        if os.path.exists(project_dir):
            self.current_project = project_name
            print(f"Проект '{project_name}' открыт")
        else:
            raise FileNotFoundError(f"Проект '{project_name}' не найден")
    
    def save_project_state(self, analysis_data, method_name: str, state_name: str = "current_state"):
        """Сохраняет текущее состояние проекта"""
        if not self.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_path, self.current_project)
        state_file = os.path.join(project_dir, f"{state_name}.json")
        
        state_data = {
            "timestamp": datetime.now().isoformat(),
            "method": method_name,
            "analysis_data": analysis_data.__dict__ if hasattr(analysis_data, '__dict__') else str(analysis_data)
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)
        
        print(f"Состояние проекта '{state_name}' сохранено")
    
    def load_project_state(self, state_name: str = "current_state"):
        """Загружает состояние проекта"""
        if not self.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_path, self.current_project)
        state_file = os.path.join(project_dir, f"{state_name}.json")
        
        if not os.path.exists(state_file):
            raise FileNotFoundError(f"Состояние '{state_name}' не найдено")
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        return state_data


class CommentSystem:
    """
    Система комментариев к результатам анализа
    """
    
    def __init__(self, project_manager: ProjectManager):
        self.project_manager = project_manager
        self.comments_file = "comments.json"
    
    def add_comment(self, analysis_id: str, comment: str, author: str = "Anonymous"):
        """Добавляет комментарий к результатам анализа"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        comments_path = os.path.join(project_dir, self.comments_file)
        
        # Загружаем существующие комментарии или создаем новый список
        if os.path.exists(comments_path):
            with open(comments_path, 'r', encoding='utf-8') as f:
                comments = json.load(f)
        else:
            comments = {}
        
        # Создаем запись комментария
        comment_entry = {
            "id": len(comments.get(analysis_id, [])),
            "comment": comment,
            "author": author,
            "timestamp": datetime.now().isoformat()
        }
        
        # Добавляем комментарий к соответствующему анализу
        if analysis_id not in comments:
            comments[analysis_id] = []
        
        comments[analysis_id].append(comment_entry)
        
        # Сохраняем обновленные комментарии
        with open(comments_path, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        
        print(f"Комментарий добавлен к анализу '{analysis_id}'")
    
    def get_comments(self, analysis_id: str) -> List[Dict]:
        """Получает все комментарии для конкретного анализа"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        comments_path = os.path.join(project_dir, self.comments_file)
        
        if not os.path.exists(comments_path):
            return []
        
        with open(comments_path, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        
        return comments.get(analysis_id, [])
    
    def delete_comment(self, analysis_id: str, comment_id: int):
        """Удаляет комментарий по ID"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        comments_path = os.path.join(project_dir, self.comments_file)
        
        if not os.path.exists(comments_path):
            raise FileNotFoundError(f"Файл комментариев не найден")
        
        with open(comments_path, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        
        if analysis_id in comments and len(comments[analysis_id]) > comment_id:
            del comments[analysis_id][comment_id]
            
            with open(comments_path, 'w', encoding='utf-8') as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)
            
            print(f"Комментарий {comment_id} удален из анализа '{analysis_id}'")
        else:
            raise IndexError(f"Комментарий с ID {comment_id} не найден в анализе '{analysis_id}'")


class VersionControl:
    """
    Система версионирования аналитических моделей
    """
    
    def __init__(self, project_manager: ProjectManager):
        self.project_manager = project_manager
        self.version_history_file = "version_history.json"
    
    def create_version(self, model_data, version_description: str = "", version_number: str = None):
        """Создает новую версию модели"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        versions_dir = os.path.join(project_dir, "versions")
        
        if not os.path.exists(versions_dir):
            os.makedirs(versions_dir)
        
        # Генерируем номер версии если он не предоставлен
        if not version_number:
            version_number = self._generate_version_number()
        
        # Сохраняем данные модели в файл версии
        version_filename = f"model_v{version_number.replace('.', '_')}.json"
        version_path = os.path.join(versions_dir, version_filename)
        
        version_data = {
            "version": version_number,
            "description": version_description,
            "timestamp": datetime.now().isoformat(),
            "model_data": model_data.__dict__ if hasattr(model_data, '__dict__') else str(model_data)
        }
        
        with open(version_path, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
        
        # Обновляем историю версий
        self._update_version_history(version_number, version_description)
        
        print(f"Версия {version_number} модели создана")
    
    def _generate_version_number(self) -> str:
        """Генерирует следующий номер версии"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        versions_dir = os.path.join(project_dir, "versions")
        
        if not os.path.exists(versions_dir):
            return "1.0.0"
        
        # Ищем последнюю версию
        version_files = [f for f in os.listdir(versions_dir) if f.startswith("model_v") and f.endswith(".json")]
        
        if not version_files:
            return "1.0.0"
        
        # Получаем номера версий из имен файлов
        version_numbers = []
        for vf in version_files:
            # Извлекаем номер версии из имени файла (например, из "model_v1_0_0.json" получаем "1.0.0")
            version_part = vf.replace("model_v", "").replace(".json", "")
            version_number = version_part.replace("_", ".")
            version_numbers.append(version_number)
        
        # Находим максимальную версию и увеличиваем
        max_version = max(version_numbers, key=lambda x: [int(part) for part in x.split('.')])
        parts = max_version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)  # Увеличиваем патч-версию
        
        return ".".join(parts)
    
    def _update_version_history(self, version_number: str, description: str):
        """Обновляет историю версий"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        history_path = os.path.join(project_dir, self.version_history_file)
        
        # Загружаем существующую историю
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        # Добавляем новую запись в историю
        history.append({
            "version": version_number,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
        # Сохраняем обновленную историю
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_version_history(self) -> List[Dict]:
        """Получает историю всех версий"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        history_path = os.path.join(project_dir, self.version_history_file)
        
        if not os.path.exists(history_path):
            return []
        
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_version(self, version_number: str):
        """Загружает данные модели определенной версии"""
        if not self.project_manager.current_project:
            raise ValueError("Нет активного проекта")
        
        project_dir = os.path.join(self.project_manager.project_path, self.project_manager.current_project)
        versions_dir = os.path.join(project_dir, "versions")
        
        version_filename = f"model_v{version_number.replace('.', '_')}.json"
        version_path = os.path.join(versions_dir, version_filename)
        
        if not os.path.exists(version_path):
            raise FileNotFoundError(f"Версия {version_number} не найдена")
        
        with open(version_path, 'r', encoding='utf-8') as f:
            version_data = json.load(f)
        
        return version_data["model_data"]