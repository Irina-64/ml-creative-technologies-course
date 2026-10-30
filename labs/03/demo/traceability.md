| Требование | Источник знания | Проверка | Артефакт |
|---|---|---|---|
| R1 Поиск | K2, гипотеза о словах | T1 нормальный и синонимический запросы | demo/results/api_examples.json |
| R2 Источник | K1 | T2 проверка полей карточки | контракт ЛР 11 |
| R3 Допуск | K1 | test_rights_filter_defense | demo/test_project.py |
| R4 Исправление | K3 | test_feedback_does_not_train | demo/results/feedback_examples.json |
| R5 Ошибки | Граница alpha из ЛР 1 | test_invalid_input и test_fallback_visible | demo/test_project.py |

Результат ЛР 3 — спецификация. Факт реализации подтверждается в последующих работах. Это различие нужно сохранить в отчёте: наличие требования ещё не означает прохождение теста.
