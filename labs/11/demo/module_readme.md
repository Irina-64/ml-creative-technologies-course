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
