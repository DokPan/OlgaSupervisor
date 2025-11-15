DIALOGS_FILE = "data/Файл с транскибированными диалогами.xlsx"
FIRST_PASS_FILE = "output/first_pass_errors.xlsx"
FINAL_RESULTS_FILE = "output/final_confirmed_errors.xlsx"

POSITIVE_PHRASES = [
    "да планируем", 
    "будем пользоваться", 
    "конечно будем", 
    "остаёмся", 
    "продолжаем", 
    "планируем дальше",
    "будем сотрудничать",
    "да",  
    "конечно",  
    "естественно"  
]

NEGATIVE_PHRASES = [
    "нет не планируем", 
    "уходим", 
    "не будем",
    "отказываемся", 
    "не буду пользоваться",
    "больше не буду",
    "нет",  
    "не" 
]

UNCLEAR_PHRASES = [
    "ну...", 
    "нууу", 
    "не знаю", 
    "пока не могу",
    "не уверен", 
    "сомневаюсь", 
    "надо подумать",
    "не определился"
]

WRONG_PERSON_PHRASES = [
    "не председатель", 
    "не мой договор", 
    "ошиблись номером",
    "не являюсь", 
    "не тот человек",
    "я не занимаюсь"
]

PROBLEMATIC_PROMPTS = [
    'clarification_default', 
    'clarification_dont_understand', 
    'clarification_null',
    'clarification_what_company', 
    'clarification_already_phoned'
]