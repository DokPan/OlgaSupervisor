import pandas as pd
import re

class ErrorCategorizer:
    def __init__(self):
        self.categories = {
            'wrong_person': 'Неправильный собеседник',
            'communication_breakdown': 'Серьезные проблемы коммуникации', 
            'false_positive_churn': 'Ложный отток (клиент соглашается)',
            'uncertain_churn': 'Неопределенность при оттоке',
            'ignored_questions': 'Игнорирование критических вопросов',
            'false_negative_churn': 'Клиент отказывается, но статус не отток'
        }

    def categorize_errors(self, df, total_dialogs):
        print("Категоризация ошибок...")
        
        if len(df) == 0:
            print("Нет ошибок для категоризации")
            return df
            
        categorized_errors = []
        
        for idx, row in df.iterrows():
            category = self._determine_category(row)
            categorized_row = row.copy()
            categorized_row['Категория ошибки'] = category
            categorized_errors.append(categorized_row)
        
        result_df = pd.DataFrame(categorized_errors)
        
        self._print_category_statistics(result_df, total_dialogs)
        
        return result_df
    
    def _determine_category(self, row):
        reason = str(row.get('Причина ошибки', ''))
        
        if 'Неправильный собеседник' in reason:
            return self.categories['wrong_person']
        if 'Ложный отток (клиент соглашается)' in reason:
            return self.categories['false_positive_churn']
        if 'Клиент отказывается, но статус не отток' in reason:
            return self.categories['false_negative_churn']
        if 'Неопределенность при оттоке' in reason:
            return self.categories['uncertain_churn']
        if 'Серьезные проблемы коммуникации' in reason:
            return self.categories['communication_breakdown']
        if 'Игнорирование критических вопросов' in reason:
            return self.categories['ignored_questions']
        
        if ' | ' in reason:
            return reason.split(' | ')[0]
        return reason

    def _print_category_statistics(self, df, total_dialogs):
        print("\nСТАТИСТИКА ПО КАТЕГОРИЯМ ОШИБОК:")
        print("=" * 50)
        
        total_errors = len(df)
        category_counts = df['Категория ошибки'].value_counts()
        
        overall_error_percentage = (total_errors / total_dialogs) * 100
        
        print(f"Всего диалогов: {total_dialogs:,}")
        print(f"Найдено ошибок: {total_errors:,}")
        print(f"Процент ошибок: {overall_error_percentage:.1f}%")
        print("\nРаспределение по категориям (от всех диалогов):")
        
        for category, count in category_counts.items():
            percentage = (count / total_dialogs) * 100
            print(f"  {category}: {count:,} ({percentage:.1f}%)")
        
        print("\nАНАЛИТИКА:")
        if total_errors > 0:
            main_category = category_counts.index[0]
            main_count = category_counts.iloc[0]
            main_percentage_from_errors = (main_count / total_errors) * 100
            print(f"  Основная проблема: {main_category} ({main_percentage_from_errors:.1f}% всех ошибок)")