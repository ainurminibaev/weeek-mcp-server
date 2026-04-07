# Деплой Weeek MCP Server (наши доработки)

Форк [AlekMel/weeek-mcp-server](https://github.com/AlekMel/weeek-mcp-server) с доработками для multi-workspace и Claude Desktop.

## Что мы добавили поверх оригинала

### 1. Multi-workspace через X-Weeek-Token
Один сервер обслуживает несколько workspace. Каждый клиент передаёт свой Weeek API токен в заголовке `X-Weeek-Token` — сервер использует его для запросов к Weeek API вместо серверного `WEEEK_TOKEN`.

**Изменённые файлы:**
- `src/config.py` — `WEEEK_TOKEN` стал опциональным
- `src/weeek_client.py` — добавлен `ContextVar` для per-request токена
- `src/server.py` — добавлен `WeeekTokenMiddleware`

### 2. Query-параметры для авторизации
Claude Desktop connector не поддерживает кастомные заголовки. Добавлена поддержка авторизации через URL query-параметры:
- `?api_key=...` — вместо `Authorization: Bearer ...`
- `?weeek_token=...` — вместо `X-Weeek-Token: ...`

**Изменённый файл:** `src/server.py` (оба middleware)

### 3. HTTPS через nginx
Порт 3847 привязан к localhost, весь внешний трафик через nginx + Let's Encrypt.

---

## Деплой на VPS

### Требования
- VPS с Docker и Docker Compose
- Домен с DNS A-записью на IP сервера
- nginx + certbot

### Шаг 1: Клонировать и настроить

```bash
cd /opt
git clone https://github.com/AlekMel/weeek-mcp-server.git weeek-mcp
cd weeek-mcp
```

### Шаг 2: Создать .env

```bash
cp deploy/.env.example .env
nano .env
```

```env
MCP_API_KEY=сгенерируй_ключ_минимум_32_символа
```

Сгенерировать ключ:
```bash
python3 -c "import secrets; print(secrets.token_hex(24))"
```

### Шаг 3: docker-compose.yml

Используй `deploy/docker-compose.yml` или создай в корне:

```yaml
services:
  weeek:
    build: .
    container_name: weeek-mcp
    restart: unless-stopped
    ports:
      - "127.0.0.1:3847:3847"
    environment:
      - WEEEK_BASE_URL=https://api.weeek.net/public/v1
      - TRANSPORT=sse
      - HOST=0.0.0.0
      - PORT=3847
      - MCP_API_KEY=${MCP_API_KEY}
      - REQUEST_TIMEOUT=30
      - LOG_LEVEL=INFO
```

Порт `127.0.0.1:3847` — только localhost, наружу через nginx.

### Шаг 4: Запуск

```bash
docker compose up -d --build
curl http://127.0.0.1:3847/health
```

### Шаг 5: nginx + HTTPS

Скопировать конфиг:
```bash
cp deploy/nginx-weeek.conf /etc/nginx/sites-available/weeek
ln -s /etc/nginx/sites-available/weeek /etc/nginx/sites-enabled/
```

Отредактировать `server_name` на свой домен, затем:
```bash
certbot --nginx -d yourdomain.com
nginx -t && systemctl reload nginx
```

Конфиг nginx отключает логирование (чтобы токены из query-параметров не попали в логи):
```nginx
location / {
    access_log off;
    proxy_pass http://127.0.0.1:3847;
    ...
}
```

---

## Подключение клиентов

### Claude Code (CLI)

```bash
claude mcp add weeek-marusya \
  --transport sse \
  --url https://yourdomain.com/sse \
  --header "Authorization: Bearer YOUR_MCP_API_KEY" \
  --header "X-Weeek-Token: YOUR_WEEEK_TOKEN"
```

### Claude Desktop (через mcp-remote)

Claude Desktop connector UI не поддерживает кастомные заголовки. Используем `mcp-remote` как мост.

**Требуется:** Node.js ([nodejs.org](https://nodejs.org), проверка: `node -v`).

#### macOS

Файл конфига: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weeek-marusya": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://yourdomain.com/sse",
        "--header",
        "Authorization: Bearer YOUR_MCP_API_KEY",
        "--header",
        "X-Weeek-Token: YOUR_WEEEK_TOKEN"
      ]
    }
  }
}
```

#### Windows

Файл конфига: `%APPDATA%\Claude\claude_desktop_config.json`

На Windows используй `npx.cmd` вместо `npx`:

```json
{
  "mcpServers": {
    "weeek-marusya": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "mcp-remote",
        "https://yourdomain.com/sse",
        "--header",
        "Authorization: Bearer YOUR_MCP_API_KEY",
        "--header",
        "X-Weeek-Token: YOUR_WEEEK_TOKEN"
      ]
    }
  }
}
```

После сохранения — перезапустить Claude Desktop.

### Cursor IDE

В `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "weeek": {
      "url": "https://yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY",
        "X-Weeek-Token": "YOUR_WEEEK_TOKEN"
      }
    }
  }
}
```

---

## Multi-workspace: несколько пространств через один сервер

Каждый пользователь передаёт свой `X-Weeek-Token`. Один сервер, разные workspace.

#### macOS

```json
{
  "mcpServers": {
    "weeek-team": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://yourdomain.com/sse",
        "--header", "Authorization: Bearer ОБЩИЙ_MCP_API_KEY",
        "--header", "X-Weeek-Token: ТОКЕН_WORKSPACE_КОМАНДЫ"
      ]
    },
    "weeek-personal": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://yourdomain.com/sse",
        "--header", "Authorization: Bearer ОБЩИЙ_MCP_API_KEY",
        "--header", "X-Weeek-Token: ТОКЕН_ЛИЧНОГО_WORKSPACE"
      ]
    }
  }
}
```

#### Windows

То же самое, но `"command": "npx.cmd"` вместо `"command": "npx"`.

---

## Где взять Weeek API Token

1. Зайди в https://app.weeek.net
2. Настройки (шестерёнка) → API
3. Создай новый токен
4. Скопируй

---

## Известные ограничения Weeek API

- `priority` при создании задачи принимает только `int`, не строку — лучше не передавать через MCP
- `description` можно задать только при создании (POST), update (PUT) его не обновляет
- Описание должно быть в HTML: `<p>текст</p>`

---

## Безопасность

- Порт 3847 слушает только localhost — наружу только через HTTPS nginx
- `MCP_API_KEY` — защита от неавторизованного доступа к серверу
- `X-Weeek-Token` — per-user токен, не хранится на сервере
- nginx access_log отключен (токены в query-параметрах не логируются)
- HTTPS шифрует весь URL включая query-параметры
