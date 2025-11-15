import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

class BusinessVisualizer:
    def __init__(self):
        self.pastel_colors = ['#FFB7C5', '#A2D2FF', '#BDE0FE', '#FFAFCC', '#CDB4DB']
        
        plt.style.use('default')
        self.set_elegant_style()
    
    def set_elegant_style(self):
        plt.rcParams['figure.facecolor'] = '#FAFAFA'
        plt.rcParams['axes.facecolor'] = '#FFFFFF'
        plt.rcParams['grid.color'] = '#E0E0E0'
        plt.rcParams['grid.alpha'] = 0.2
        plt.rcParams['text.color'] = '#37474F'
        plt.rcParams['axes.labelcolor'] = '#546E7A'
        plt.rcParams['xtick.color'] = '#546E7A'
        plt.rcParams['ytick.color'] = '#546E7A'
    
    def create_accuracy_analysis_chart(self, errors_df, total_dialogs, save_path="output/accuracy_analysis.png"):
        error_count = len(errors_df) if not errors_df.empty else 0
        accuracy_percentage = ((total_dialogs - error_count) / total_dialogs) * 100
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sizes = [error_count, total_dialogs - error_count]
        labels = [f'Ошибки\n{error_count}', f'Корректные\n{total_dialogs - error_count}']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=self.pastel_colors[:2],
                                          autopct='%1.1f%%', startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(f'Точность классификации робота\n{accuracy_percentage:.1f}% диалогов обработано верно', 
                     fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#FAFAFA')
        plt.close()
        
        return save_path

    def create_error_priority_chart(self, errors_df, total_dialogs, save_path="output/error_priority.png"):
        if errors_df.empty:
            return None
        
        error_counts = errors_df['Категория ошибки'].value_counts()
        
        priority_data = []
        for category, count in error_counts.items():
            percentage = (count / total_dialogs) * 100
            
            if percentage >= 5:
                priority_level = "Критический"
                color = self.pastel_colors[0]
            elif percentage >= 2:
                priority_level = "Высокий"
                color = self.pastel_colors[1]
            elif percentage >= 1:
                priority_level = "Средний" 
                color = self.pastel_colors[2]
            else:
                priority_level = "Низкий"
                color = self.pastel_colors[4]
                
            priority_data.append({
                'Категория': category,
                'Количество': count,
                'Процент': percentage,
                'Приоритет': priority_level,
                'Цвет': color
            })
        
        priority_data.sort(key=lambda x: x['Процент'], reverse=True)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        categories = [f"{item['Категория']}" for item in priority_data]
        counts = [item['Количество'] for item in priority_data]
        colors = [item['Цвет'] for item in priority_data]
        
        bars = ax.barh(categories, counts, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
        
        for i, (category, count, item) in enumerate(zip(categories, counts, priority_data)):
            ax.text(count + 0.1, i, f'{count} ({item["Процент"]:.1f}%)', 
                   va='center', ha='left', fontweight='bold', fontsize=10)
        
        ax.set_xlabel('Количество ошибок')
        ax.set_title('Приоритеты исправления ошибок классификации\n(проценты от общего числа диалогов)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        legend_elements = [
            plt.Rectangle((0,0),1,1, fc=self.pastel_colors[0], alpha=0.8, label='Критический (≥5%)'),
            plt.Rectangle((0,0),1,1, fc=self.pastel_colors[1], alpha=0.8, label='Высокий (2-5%)'),
            plt.Rectangle((0,0),1,1, fc=self.pastel_colors[2], alpha=0.8, label='Средний (1-2%)'),
            plt.Rectangle((0,0),1,1, fc=self.pastel_colors[4], alpha=0.8, label='Низкий (<1%)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#FAFAFA')
        plt.close()
        
        return save_path

    def create_all_charts(self, errors_df, total_dialogs):
        charts = {}
        
        charts['accuracy_analysis'] = self.create_accuracy_analysis_chart(errors_df, total_dialogs)
        
        if not errors_df.empty:
            charts['error_priority'] = self.create_error_priority_chart(errors_df, total_dialogs)
        
        return charts