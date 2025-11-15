def select_recommendation_type():
    print("\nВыберите тип рекомендаций:")
    print("1. AI-рекомендации (GigaChat)")
    print("2. Без рекомендаций")
    
    while True:
        choice = input("\nВведите номер (1-2, по умолчанию 1): ").strip()
        
        if choice == "" or choice == "1":
            return "ai"
        elif choice == "2":
            return "none"
        else:
            print("Неверный выбор. Попробуйте снова.")