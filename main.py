import pandas as pd
import os
from improved_analyzer import DoubleCheckAnalyzer
from config import DIALOGS_FILE, FINAL_RESULTS_FILE
from script_generator import ScriptGenerator
from visualizer import BusinessVisualizer

def main():
    print("OlgaSupervisor Анализатор ошибок классификации")
    print("=" * 60)
    
    os.makedirs('output', exist_ok=True)
    
    if os.path.exists(FINAL_RESULTS_FILE):
        os.remove(FINAL_RESULTS_FILE)
        print(f"Удален предыдущий файл: {FINAL_RESULTS_FILE}")
    
    if not os.path.exists(DIALOGS_FILE):
        print(f"Файл с диалогами не найден: {DIALOGS_FILE}")
        return
    
    print("Загрузка диалогов...")
    try:
        df = pd.read_excel(DIALOGS_FILE)
        total_dialogs = len(df)
        print(f"Загружено диалогов: {total_dialogs:,}")
        
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return
    
    analyzer = DoubleCheckAnalyzer()
    
    print("\n" + "="*50)
    print("АНАЛИЗ ОШИБОК КЛАССИФИКАЦИИ")
    
    final_results, detailed_results = analyzer.first_pass_analysis(df)
    
    if final_results is not None and len(final_results) > 0:
        final_results.to_excel(FINAL_RESULTS_FILE, index=False)
        print(f"Основные ошибки сохранены: {FINAL_RESULTS_FILE}")
        
        print("\n" + "="*50)
        print("КОРРЕКЦИЯ СТАТУСОВ И СОЗДАНИЕ ДОПОЛНИТЕЛЬНЫХ ФАЙЛОВ")
        
        correction_results = analyze_and_correct_errors()
        
        if correction_results is not None:
            summary = generate_summary_report(correction_results)
            create_corrected_dialogs_file(correction_results, DIALOGS_FILE)
            print(f"Коррекция завершена! Созданы дополнительные файлы:")
            print(f"    output/correction_table.xlsx - полная таблица исправлений")
            print(f"    output/correction_summary.xlsx - сводный отчет")
            print(f"    output/dialogs_with_corrected_status.xlsx - диалоги с верными статусами")
        
        print("\n" + "="*50)
        print("СОЗДАНИЕ ГРАФИКОВ")
        
        visualizer = BusinessVisualizer()
        charts = visualizer.create_all_charts(final_results, total_dialogs)
        print(f"Создано графиков: {len(charts)}")
        
        print("\n" + "="*50)
        print("ГЕНЕРАЦИЯ СКРИПТОВ ДЛЯ ИСПРАВЛЕНИЯ ОШИБОК")
        
        script_generator = ScriptGenerator()
        scripts_generated = script_generator.generate_scripts_from_errors(final_results)
        
        if scripts_generated:
            print("Скрипты для улучшения логики сгенерированы!")
        else:
            print("Скрипты уже были сгенерированы ранее")
        
        print("\n" + "="*50)
        print("АНАЛИЗ ЭФФЕКТИВНОСТИ КОРРЕКЦИИ")
        print("=" * 50)
        
        status_changes = (correction_results['Было_статус'] != correction_results['Стало_статус']).sum()
        result_changes = (correction_results['Было_result'] != correction_results['Стало_result']).sum()
        
        print(f"Статусов исправлено: {status_changes:,} из {len(correction_results):,}")
        print(f"Result исправлен: {result_changes:,} из {len(correction_results):,}")
        
        correction_rate = (status_changes / len(correction_results)) * 100
        print(f"Эффективность коррекции: {correction_rate:.1f}%")
        
        if correction_rate > 80:
            print("Высокая эффективность коррекции!")
        elif correction_rate > 60:
            print("Средняя эффективность коррекции")
        else:
            print("Низкая эффективность коррекции")
            
    else:
        print("Ошибок не найдено")
        visualizer = BusinessVisualizer()
        visualizer.create_accuracy_analysis_chart(pd.DataFrame(), total_dialogs)
        print("Создан график с результатами анализа")

def analyze_and_correct_errors():
    print("Запуск коррекции статусов...")
    
    try:
        df = pd.read_excel('output/final_confirmed_errors.xlsx')
        print(f"Загружено подтвержденных ошибок: {len(df):,}")
    except Exception as e:
        print(f"Ошибка загрузки файла: {e}")
        
        print("\nДоступные файлы:")
        files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        for file in files:
            print(f"    {file}")
        return None

    required_columns = ['Номер клиента', 'Статус', 'Result', 'call_transcript', 'Категория ошибки']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Отсутствуют колонки: {missing_columns}")
        print(f"Доступные колонки: {list(df.columns)}")
        return None
    
    correction_data = []
    
    print(f"Анализ и коррекция статусов...")
    
    for index, row in df.iterrows():
        client_id = row['Номер клиента']
        original_status = row['Статус']
        original_result = row['Result']
        error_category = row['Категория ошибки']
        transcript = str(row['call_transcript'])
        
        corrected_status, corrected_result, correction_reason = analyze_and_correct(
            original_status, original_result, error_category, transcript
        )
        
        correction_data.append({
            'Номер клиента': client_id,
            'Было_статус': original_status,
            'Стало_статус': corrected_status,
            'Было_result': original_result,
            'Стало_result': corrected_result,
            'Тип_ошибки': error_category,
            'Причина_коррекции': correction_reason,
            'call_transcript': transcript
        })
    
    correction_df = pd.DataFrame(correction_data)
    output_file = "output/correction_table.xlsx"
    correction_df.to_excel(output_file, index=False)
    
    status_changes = (correction_df['Было_статус'] != correction_df['Стало_статус']).sum()
    result_changes = (correction_df['Было_result'] != correction_df['Стало_result']).sum()
    
    print(f"Результаты коррекции:")
    print(f"   Всего записей: {len(correction_df):,}")
    print(f"   Статусов изменено: {status_changes:,}")
    print(f"   Result изменен: {result_changes:,}")
    
    print(f"Таблица исправлений сохранена: {output_file}")
    
    return correction_df

def analyze_and_correct(original_status, original_result, error_category, transcript):
    corrected_status = original_status
    corrected_result = original_result
    correction_reason = "Без изменений"
    
    if error_category == "Ложный отток (клиент соглашается)":
        if "подтверждена" in str(original_status).lower():
            corrected_status = "угроза оттока не подтверждена"
            corrected_result = "согласие - да"
            correction_reason = "Клиент соглашается, но был помечен как отток"
    
    elif error_category == "Серьезные проблемы коммуникации":
        corrected_status = "угроза оттока не определена, требуется уточнение"
        corrected_result = "отказ - проблемы связи"
        correction_reason = "Критические проблемы коммуникации"
    
    elif error_category == "Неправильный собеседник":
        corrected_status = "угроза оттока не определена_ неверный контакт"
        corrected_result = "ошиблись номером"
        correction_reason = "Диалог с лицом, не принимающим решения"
    
    elif error_category == "Неопределенность при оттоке":
        corrected_status = "угроза оттока требует уточнения"
        corrected_result = "отказ - не определён"
        correction_reason = "Клиент выражает сомнения"
    
    elif error_category == "Игнорирование критических вопросов":
        corrected_status = "угроза оттока подтверждена"
        corrected_result = "отказ - уклонение от ответа"
        correction_reason = "Клиент игнорирует ключевые вопросы"
    
    return corrected_status, corrected_result, correction_reason

def generate_summary_report(correction_df):
    print(f"Генерация сводного отчета...")
    summary = correction_df.groupby('Тип_ошибки').agg({
        'Номер клиента': 'count',
        'Было_статус': 'first',
        'Стало_статус': 'first'
    }).rename(columns={'Номер клиента': 'Количество'})
    
    summary['Процент'] = (summary['Количество'] / len(correction_df)) * 100
    
    summary_file = "output/correction_summary.xlsx"
    summary.to_excel(summary_file)
    
    print(f"Сводный отчет сохранен: {summary_file}")
    
    return summary

def create_corrected_dialogs_file(correction_df, original_file_path):
    print("Создание файла с верными статусами...")
    
    try:
        original_df = pd.read_excel(original_file_path)
        print(f"Загружен исходный файл: {original_file_path}")
        print(f"Записей в исходном файле: {len(original_df):,}")
    except Exception as e:
        print(f"Ошибка загрузки исходного файла: {e}")
        return
    
    correction_dict = dict(zip(correction_df['Номер клиента'], correction_df['Стало_статус']))
    
    if 'Верный статус' not in original_df.columns:
        original_df['Верный статус'] = ''
    
    original_df['Верный статус'] = original_df['Номер клиента'].map(correction_dict).fillna('')
    
    corrected_count = original_df['Верный статус'].notna().sum()
    
    output_file = "output/dialogs_with_corrected_status.xlsx"
    original_df.to_excel(output_file, index=False)
    
    print(f"Файл с верными статусами создан: {output_file}")
    print(f"Заполнено верных статусов: {corrected_count:,} из {len(original_df):,}")

if __name__ == "__main__":
    main()
    print("\nПрограмма завершена!")