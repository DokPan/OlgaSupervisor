import pandas as pd
import re
from typing import Dict, List
import os
from .gigachat_generator import GigaChatGenerator

class ScriptGenerator:
    
    def __init__(self):
        self.ai_enabled = os.getenv('AI_ENABLED', 'true').lower() == 'true'
        self.ai_provider = os.getenv('AI_PROVIDER', 'gigachat')
        self.ai_generator = None
        self._scripts_generated = False
    
    def _initialize_ai(self):
        if self.ai_generator is None and self.ai_enabled and self.ai_provider == 'gigachat':
            try:
                self.ai_generator = GigaChatGenerator()
                print("Настоящий ИИ (GigaChat) активирован!")
            except Exception as e:
                print(f"GigaChat не доступен: {e}")
                self.ai_generator = None
    
    def generate_scripts_from_errors(self, errors_df: pd.DataFrame, recommendation_type="ai"):
        if self._scripts_generated:
            print("Рекомендации уже были сгенерированы ранее")
            return False
            
        print(f"Генерация рекомендаций ({recommendation_type})...")
        
        if len(errors_df) == 0:
            print("Нет ошибок для генерации рекомендаций")
            return False
        
        if recommendation_type == "ai":
            self._initialize_ai()
        
        category_stats = errors_df['Категория ошибки'].value_counts()
        
        solutions = self._generate_category_solutions(category_stats, errors_df, recommendation_type)
        
        self._save_solutions_to_file(solutions, len(errors_df), recommendation_type)
        
        print(f"Рекомендации ({recommendation_type}) сгенерированы!")
        self._scripts_generated = True
        return True

    def _generate_category_solutions(self, category_stats, errors_df, recommendation_type) -> List[Dict]:
        solutions = []
        
        for category, count in category_stats.items():
            examples = self._get_category_examples(errors_df, category)
            
            if recommendation_type == "ai":
                solution = self._create_ai_solution(category, count, examples)
            else:
                solution = self._create_statistics_only(category, count, examples)
                
            solutions.append(solution)
        
        return solutions

    def _get_category_examples(self, errors_df, category, max_examples=2):
        category_errors = errors_df[errors_df['Категория ошибки'] == category]
        examples = []
        
        for _, row in category_errors.head(max_examples).iterrows():
            transcript = str(row['call_transcript'])
            excerpt = self._extract_dialog_excerpt(transcript)
            if excerpt:
                examples.append(excerpt)
        
        return examples

    def _extract_dialog_excerpt(self, transcript: str) -> str:
        lines = [line.strip() for line in transcript.split(';') if line.strip()]
        if len(lines) >= 2:
            return '\n'.join(lines[-2:])
        return transcript[:200] + '...' if len(transcript) > 200 else transcript

    def _create_ai_solution(self, category: str, count: int, examples: List[str]) -> Dict:
        if self.ai_generator:
            ai_response = self.ai_generator.generate_script(category, count, count, examples)
            return {'category': category, 'solution': ai_response}
        else:
            print(f"AI недоступен, рекомендации не сгенерированы для категории '{category}'")
            return self._create_statistics_only(category, count, examples)

    def _create_statistics_only(self, category: str, count: int, examples: List[str]) -> Dict:
        solution = f"""
КАТЕГОРИЯ: {category}
КОЛИЧЕСТВО ОШИБОК: {count}
ПРИМЕРОВ ПРОАНАЛИЗИРОВАНО: {len(examples)}

Рекомендации не требуются.
"""
        return {'category': category, 'solution': solution.strip()}

    def _save_solutions_to_file(self, solutions: List[Dict], total_errors: int, recommendation_type: str):
        try:
            filename = f"output/рекомендации_{recommendation_type}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"РЕКОМЕНДАЦИИ ДЛЯ ИСПРАВЛЕНИЯ ОШИБОК ({recommendation_type.upper()})\n")
                f.write("=" * 60 + "\n")
                f.write(f"Всего обнаружено ошибок: {total_errors}\n\n")
                
                for solution_data in solutions:
                    f.write(solution_data['solution'])
                    f.write("\n" + "=" * 60 + "\n\n")
            
            print(f"Решения сохранены: {filename}")
            print(f"Охвачено {len(solutions)} категорий ошибок")
            
        except Exception as e:
            print(f"Ошибка сохранения решений: {e}")