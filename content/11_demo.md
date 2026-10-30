## Полный демонстрационный вариант

### Артефакт Контракт
<!-- artifact: contract.md -->
POST /search принимает JSON-объект с полем query типа string. После удаления внешних пробелов допустимы 1–300 символов. Сервер читает тело не больше 4096 байт. Успешный ответ HTTP 200 содержит status, model, results, human_decision_required. Карточка содержит id, genre, style, score, source, rights_status, image.

Статусы: ok — есть совпадения; no_matches — корректный запрос, совпадений нет; fallback — применён резервный поиск. Ошибки HTTP 400: query_must_be_string, empty_query, query_too_long, object_required или ошибка JSON. Неизвестный путь возвращает 404. Score — сходство, не вероятность.

Пример входа:

```json
{"query":"саксофон лаконичный"}
```

Векторизация использует train-IDF 1.0 и lexicon 1.0. Внешняя модель и prompt template не применяются, поскольку это поисковый, а не генеративный трек.
<!-- endartifact -->

### Артефакт Запускаемый модуль и конфигурация
<!-- artifact: module_readme.md -->
```powershell
python -m demo.project run
python -m unittest demo.test_project -v
python -m demo.server --port 8765
```

В другом терминале PowerShell:

```powershell
$body = @{query='саксофон лаконичный'} | ConvertTo-Json
$bytes = [Text.Encoding]::UTF8.GetBytes($body)
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/search' -Method Post -ContentType 'application/json; charset=utf-8' -Body $bytes
```

Остановить сервер: Ctrl+C. Полная реализация состоит из demo/project.py и demo/server.py. Конфигурация demo/config.json содержит k=3, max_query_chars=300, model=tfidf+lexicon, model_version=1.0. Все параметры и данные локальны; установка сторонних пакетов для демо не требуется.
<!-- endartifact -->

### Артефакт Фактические ответы

{{api_examples}}

### Артефакт Набор сложных случаев
<!-- artifact: cases.md -->
| Вход | Ожидаемое поведение | Основание |
|---|---|---|
| джаз минимализм | 200, ok, карточки | Нормальный сценарий |
| саксофон лаконичный | 200, ok после словаря | Проверка инженерии знаний |
| jazz minimalist | 200, no_matches | Неизвестный язык |
| Пустая строка | 400, empty_query | R5 |
| 301 символ | 400, query_too_long | Контракт |
| Число 42 вместо строки | 400, query_must_be_string | Контракт |
| Массив вместо объекта | 400, object_required | Контракт |

Набор unittest проверяет ранжирование, split, неизменность IDF при изменении test, фильтр допуска, ошибки и обратную связь. Эти тесты не заменяют проверку пользовательской ценности и качества на реальном архиве.
<!-- endartifact -->
