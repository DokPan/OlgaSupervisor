import pandas as pd
import re
from config import *
from error_categorizer import ErrorCategorizer

class DoubleCheckAnalyzer:
    def __init__(self):
        self.categorizer = ErrorCategorizer()
        
        self.positive_pattern = re.compile(r'\b(да планируем|будем пользоваться|конечно будем|остаёмся|продолжаем|планируем дальше|да\b|конечно\b|естественно\b)\b', re.IGNORECASE)
        self.negative_pattern = re.compile(r'\b(нет не планируем|уходим|не будем|отказываемся|не буду пользоваться|нет\b|не\b)\b', re.IGNORECASE)
        self.unclear_pattern = re.compile(r'\b(нуу*\.{3}|не знаю|пока не могу|не уверен|сомневаюсь|надо подумать)\b', re.IGNORECASE)
        self.wrong_person_pattern = re.compile(r'\b(не председатель|не мой договор|ошиблись номером|не являюсь|не тот человек)\b', re.IGNORECASE)
    
    def first_pass_analysis(self, df):
        print("Поиск подтвержденных ошибок классификации")
        
        status_col = self._find_column(df, ['Статус', 'status'])
        result_col = self._find_column(df, ['result', 'результат'])
        transcript_col = self._find_column(df, ['call_transcript', 'транскрипт'])
        client_col = self._find_column(df, ['Номер клиента', 'client_id', 'id'])
        prompts_col = self._find_column(df, ['prompts_statistics', 'prompts'])
        duration_col = self._find_column(df, ['длительность', 'duration', 'call_duration'])
        call_status_col = self._find_column(df, ['call_status', 'статус звонка'])
        
        if not all([status_col, result_col, transcript_col, client_col]):
            print("Не найдены необходимые колонки")
            return None, None
        
        print(f"Анализ {len(df)} диалогов...")
        
        confirmed_errors = []
        detailed_errors = []
        
        for idx, row in df.iterrows():
            status = str(row[status_col])
            result = str(row[result_col])
            transcript = str(row[transcript_col])
            prompts = str(row.get(prompts_col, '')) if prompts_col else ''
            duration = str(row.get(duration_col, '')) if duration_col else ''
            call_status = str(row.get(call_status_col, '')) if call_status_col else ''
            
            error_reason = self._analyze_dialog_for_errors(status, result, transcript, prompts)
            
            if error_reason:
                confirmed_errors.append({
                    'Номер клиента': row[client_col],
                    'Статус': status,
                    'Result': result,
                    'call_transcript': transcript,
                    'Причина ошибки': error_reason
                })
                
                detailed_errors.append({
                    'Номер клиента': row[client_col],
                    'result': result,
                    'Статус': status,
                    'call_transcript': transcript,
                    'длительность': duration,
                    'call_status': call_status,
                    'prompts_statistics': prompts
                })
            
            if (idx + 1) % 1000 == 0:
                print(f"Проверено {idx + 1}/{len(df)} диалогов...")
        
        print(f"Найдено {len(confirmed_errors)} подтвержденных ошибок")
        
        if confirmed_errors:
            errors_df = pd.DataFrame(confirmed_errors)
            categorized_errors = self.categorizer.categorize_errors(errors_df, len(df))
            
            detailed_df = pd.DataFrame(detailed_errors)
            
            return categorized_errors, detailed_df
        
        return pd.DataFrame(confirmed_errors), pd.DataFrame(detailed_errors)
    
    def _analyze_dialog_for_errors(self, status, result, transcript, prompts):
        reasons = []
        status_lower = status.lower()
        transcript_lower = transcript.lower()
        
        if self.wrong_person_pattern.search(transcript_lower):
            return "Неправильный собеседник"
        
        if self._has_serious_prompt_problems(prompts, transcript):
            reasons.append("Серьезные проблемы коммуникации")
        
        client_response = self._extract_client_response(transcript)
        if client_response:
            client_response_lower = client_response.lower()
            
            if "угроза оттока подтверждена" in status_lower:
                if self.positive_pattern.search(client_response_lower):
                    if self._is_definite_positive_answer(client_response_lower):
                        reasons.append("Ложный отток (клиент соглашается)")
                elif self.unclear_pattern.search(client_response_lower) and len(reasons) == 0:
                    reasons.append("Неопределенность при оттоке")
            
            elif "угроза оттока не подтверждена" in status_lower:
                if self.negative_pattern.search(client_response_lower):
                    if self._is_definite_negative_answer(client_response_lower):
                        reasons.append("Клиент отказывается, но статус не отток")
        
        if self._has_critical_ignored_questions(transcript):
            reasons.append("Игнорирование критических вопросов")
        
        return " | ".join(reasons) if reasons else None
    
    def _is_definite_positive_answer(self, response):
        simple_positive = [' да ', ' конечно ', ' естественно ', 'да,', 'конечно,']
        return any(answer in response for answer in simple_positive)
    
    def _is_definite_negative_answer(self, response):
        simple_negative = [' нет ', ' не ', 'нет,', 'не,']
        return any(answer in response for answer in simple_negative)
    
    def _has_serious_prompt_problems(self, prompts, transcript):
        if not prompts:
            return False
            
        critical_prompts = ['clarification_default', 'clarification_dont_understand', 'clarification_null']
        problem_count = sum(1 for problem in critical_prompts if problem in prompts)
        
        if problem_count >= 2:
            return True
        elif problem_count >= 1 and self._has_dialog_problems(transcript):
            return True
            
        return False
    
    def _has_dialog_problems(self, transcript):
        problems = [
            "плохо слышно", "вас не слышно", "не понимаю", "что вы сказали",
            "повторите", "не расслышал"
        ]
        return any(problem in transcript.lower() for problem in problems)
    
    def _has_critical_ignored_questions(self, transcript):
        critical_questions = [
            "по какому контракту", "какой договор", "о какой компании",
            "кто звонит", "по какому номеру", "о каком контракте"
        ]
        
        lines = transcript.split(';')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('human:'):
                client_text = line.replace('human:', '').strip().lower()
                
                if any(question in client_text for question in critical_questions):
                    for j in range(i+1, min(i+3, len(lines))):
                        next_line = lines[j].strip()
                        if next_line.startswith('bot:'):
                            bot_response = next_line.replace('bot:', '').strip().lower()
                            if not any(question in bot_response for question in critical_questions):
                                if 'снижение трафика' in bot_response or 'планируете ли' in bot_response:
                                    return True
        return False
    
    def _extract_client_response(self, transcript):
        if not isinstance(transcript, str):
            return ""
            
        lines = transcript.split(';')
        client_response = ""
        found_key_question = False
        
        for line in lines:
            line = line.strip()
            
            if 'планируете ли вы пользоваться' in line.lower() and 'bot:' in line:
                found_key_question = True
                continue
            
            if found_key_question and line.startswith('human:'):
                answer = line.replace('human:', '').strip()
                if answer and len(answer) > 1:
                    client_response += " " + answer
                elif line.startswith('bot:') and ('планируете' in line.lower() or 'уточните' in line.lower()):
                    break
        
        return client_response.strip()
    
    def _find_column(self, df, possible_names):
        for name in possible_names:
            for col in df.columns:
                if name.lower() in str(col).lower():
                    return col
        return None