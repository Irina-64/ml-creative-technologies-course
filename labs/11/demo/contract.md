POST /search принимает JSON-объект с полем query типа string. После удаления внешних пробелов допустимы 1–300 символов. Сервер читает тело не больше 4096 байт. Успешный ответ HTTP 200 содержит status, model, results, human_decision_required. Карточка содержит id, genre, style, score, source, rights_status, image.

Статусы: ok — есть совпадения; no_matches — корректный запрос, совпадений нет; fallback — применён резервный поиск. Ошибки HTTP 400: query_must_be_string, empty_query, query_too_long, object_required или ошибка JSON. Неизвестный путь возвращает 404. Score — сходство, не вероятность.

Пример входа:

```json
{"query":"саксофон лаконичный"}
```

Векторизация использует train-IDF 1.0 и lexicon 1.0. Внешняя модель и prompt template не применяются, поскольку это поисковый, а не генеративный трек.
