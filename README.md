# 🚀 Weeek MCP Server

**Model Context Protocol (MCP) сервер для полной интеграции с Weeek API**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Описание

Weeek MCP Server — это полнофункциональный MCP сервер на Python, который интегрирует **все 71 endpoint** Weeek API v1 и предоставляет их как MCP tools для использования с AI-клиентами (Claude Desktop, Perplexity, собственные MCP-клиенты и др.).

### Ключевые возможности

- ✅ **71 инструмент** — полная интеграция всех endpoint'ов Weeek API
- ✅ **Надёжный HTTP-клиент** с retry логикой и обработкой ошибок
- ✅ **Безопасность** — автоматическое сокрытие токенов в логах
- ✅ **Типизация** — полная поддержка type hints
- ✅ **Async/await** — асинхронная архитектура
- ✅ **Docker поддержка** — готовый Dockerfile
- ✅ **SSE транспорт** — удалённый доступ через HTTP для n8n, web-клиентов

---

## 🛠 Установка

### Требования

- Python 3.10 или выше
- pip (менеджер пакетов Python)
- Аккаунт Weeek с API токеном

### Шаг 1: Клонирование и установка

```bash
# Клонировать репозиторий
git clone https://github.com/your-repo/weeek-mcp-server.git
cd weeek-mcp-server

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### Шаг 2: Получение API токена

1. Войдите в ваш аккаунт [Weeek](https://weeek.net)
2. Перейдите в **Settings** → **API**
3. Нажмите **"Add token"**
4. Дайте токену имя и скопируйте его

### Шаг 3: Настройка окружения

```bash
# Скопировать пример конфигурации
cp env.example .env

# Отредактировать .env файл
# Вставить ваш токен в WEEEK_TOKEN
```

Содержимое `.env`:
```env
WEEEK_TOKEN=your-api-token-here
WEEEK_BASE_URL=https://api.weeek.net/public/v1
REQUEST_TIMEOUT=30
RETRY_ATTEMPTS=3
LOG_LEVEL=INFO
```

---

## 🚀 Запуск

### Локальный запуск

```bash
python -m src.server
```

### Через Docker

```bash
# Сборка образа
docker build -t weeek-mcp .

# Запуск с передачей токена
docker run -e WEEEK_TOKEN="your-token" -it weeek-mcp

# Или с использованием .env файла
docker run --env-file .env -it weeek-mcp
```

### Docker Compose

```bash
# Создать .env файл из примера
cp env.example .env
# Отредактировать .env и добавить WEEEK_TOKEN

# Запуск
docker-compose up -d

# Или для сборки и запуска
docker-compose up --build -d
```

---

## 🌐 SSE режим (для удалённого доступа)

MCP сервер поддерживает два режима работы:
- **stdio** (по умолчанию) — для локальных клиентов (Claude Desktop, Cursor)
- **sse** — для сетевого доступа через HTTP (n8n, удалённые клиенты)

### Настройка SSE

```env
# В .env файле
TRANSPORT=sse
SERVER_HOST=0.0.0.0
SERVER_PORT=3847
```

### Деплой на VPS через Docker

1. **Подготовка VPS:**
```bash
# Склонировать репозиторий на VPS
git clone https://github.com/your-repo/weeek-mcp-server.git
cd weeek-mcp-server

# Создать .env файл
cp env.example .env
nano .env
```

2. **Настройка .env (ОБЯЗАТЕЛЬНО):**
```env
WEEEK_TOKEN=ваш-weeek-api-токен
TRANSPORT=sse
MCP_API_KEY=ваш-секретный-ключ-минимум-32-символа
```

Генерация безопасного API ключа:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Пример: Kx7mN9pQ2rS5tU8vW0xY3zA6bC9dE2fG
```

3. **Запуск:**
```bash
docker-compose up -d --build
```

4. **Проверка работы:**
```bash
# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Проверить health endpoint (без авторизации)
curl http://localhost:3847/health

# Проверить SSE endpoint (с авторизацией)
curl -H "Authorization: Bearer YOUR_MCP_API_KEY" http://localhost:3847/sse
```

### Доступные endpoints

| Endpoint | Описание | Авторизация |
|----------|----------|-------------|
| `http://host:3847/sse` | SSE endpoint для подключения MCP клиентов | Требуется |
| `http://host:3847/messages` | Endpoint для отправки сообщений | Требуется |
| `http://host:3847/health` | Health check endpoint | Не требуется |

### Аутентификация

Все запросы к `/sse` и `/messages` требуют API ключ. Передавайте его одним из способов:

```bash
# Способ 1: Authorization header (рекомендуется)
curl -H "Authorization: Bearer YOUR_MCP_API_KEY" http://host:3847/sse

# Способ 2: X-API-Key header
curl -H "X-API-Key: YOUR_MCP_API_KEY" http://host:3847/messages
```

### Смена порта

Если порт 3847 занят, измените в `.env`:
```env
SERVER_PORT=9999
```

И в `docker-compose.yml` обновите порты:
```yaml
ports:
  - "9999:9999"
```

---

## 🔗 Интеграция с n8n

### Подключение MCP сервера к n8n

1. **Убедитесь, что MCP сервер запущен в SSE режиме на VPS**

2. **В n8n используйте HTTP Request ноду** для вызова MCP endpoints:

```
URL: http://your-vps-ip:3847/messages
Method: POST
Headers:
  Content-Type: application/json
  Authorization: Bearer YOUR_MCP_API_KEY
Body (JSON):
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_tasks",
    "arguments": {
      "project_id": "your-project-id",
      "limit": 10
    }
  }
}
```

3. **Настройка HTTP Request ноды в n8n:**

   - **Method:** POST
   - **URL:** `http://your-vps-ip:3847/messages`
   - **Authentication:** Predefined Credential Type → Header Auth
     - Name: `Authorization`
     - Value: `Bearer YOUR_MCP_API_KEY`
   - **Body Content Type:** JSON

4. **Пример Code ноды** с авторизацией:

```javascript
// Вызов MCP tool из n8n Code ноды
const MCP_API_KEY = 'your-mcp-api-key';  // Лучше хранить в credentials

const response = await $http.request({
  method: 'POST',
  url: 'http://your-vps-ip:3847/messages',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${MCP_API_KEY}`
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: Date.now(),
    method: 'tools/call',
    params: {
      name: 'create_task',
      arguments: {
        title: 'Task from n8n',
        project_id: 'proj_123',
        priority: 'high'
      }
    }
  })
});

return response.data;
```

### Примеры вызовов из n8n

**Создание задачи:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_task",
    "arguments": {
      "title": "New task from n8n workflow",
      "project_id": "7",
      "description": "Created automatically",
      "priority": "medium"
    }
  }
}
```

**Получение списка проектов:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "list_projects",
    "arguments": {
      "limit": 50
    }
  }
}
```

**Поиск задач:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_task_global",
    "arguments": {
      "q": "urgent"
    }
  }
}
```

### Firewall / Безопасность

Для продакшена рекомендуется:

1. **Настроить firewall** — открыть порт только для IP n8n сервера:
```bash
# UFW (Ubuntu)
ufw allow from YOUR_N8N_IP to any port 3847

# iptables
iptables -A INPUT -p tcp -s YOUR_N8N_IP --dport 3847 -j ACCEPT
iptables -A INPUT -p tcp --dport 3847 -j DROP
```

2. **Использовать reverse proxy** (nginx) с SSL:
```nginx
server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3847;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

---

## 🔧 Интеграция с MCP клиентами

### Вариант 1: Локальный запуск (stdio)

Для локального запуска без Docker используйте stdio транспорт.

#### Claude Desktop

Файл конфигурации:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weeek": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/weeek-mcp-server",
      "env": {
        "WEEEK_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

#### Cursor IDE

Добавьте в `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "weeek": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/weeek-mcp-server",
      "env": {
        "WEEEK_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

---

### Вариант 2: Подключение к локальному Docker (SSE)

Если MCP сервер запущен в Docker на том же компьютере, используйте SSE транспорт.

#### 1. Запустите Docker контейнер

```bash
cd weeek-mcp-server

# Создайте .env с настройками
cp env.example .env
# Отредактируйте: добавьте WEEEK_TOKEN и MCP_API_KEY

# Запустите контейнер
docker-compose up -d --build
```

#### 2. Настройка Claude Desktop (SSE)

```json
{
  "mcpServers": {
    "weeek": {
      "url": "http://localhost:3847/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

**Примечание:** Замените `YOUR_MCP_API_KEY` на значение из вашего `.env` файла.

#### 3. Настройка Cursor IDE (SSE)

В файле `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "weeek": {
      "url": "http://localhost:3847/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

#### 4. Проверка подключения

```bash
# Проверить что контейнер запущен
docker-compose ps

# Проверить health endpoint
curl http://localhost:3847/health

# Проверить SSE с авторизацией
curl -H "Authorization: Bearer YOUR_MCP_API_KEY" http://localhost:3847/sse
```

После настройки перезапустите Claude Desktop или Cursor для применения изменений.

---

### Вариант 3: Подключение к удалённому серверу (SSE)

Для подключения к MCP серверу на VPS используйте его внешний IP или домен.

#### Claude Desktop

```json
{
  "mcpServers": {
    "weeek": {
      "url": "http://YOUR_VPS_IP:3847/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

#### Cursor IDE

```json
{
  "mcpServers": {
    "weeek": {
      "url": "http://YOUR_VPS_IP:3847/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

**С SSL (рекомендуется для продакшена):**

```json
{
  "mcpServers": {
    "weeek": {
      "url": "https://mcp.yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_API_KEY"
      }
    }
  }
}
```

---

## 📚 Полный список инструментов (71 tool)

### Workspace (1)
| Tool | Описание |
|------|----------|
| `get_workspace` | Получить информацию о рабочем пространстве |

### Users (5)
| Tool | Описание |
|------|----------|
| `get_current_user` | Получить текущего пользователя |
| `list_users` | Список пользователей |
| `get_user_by_id` | Получить пользователя по ID |
| `update_user` | Обновить пользователя |
| `delete_user` | Удалить пользователя |

### Tags (4)
| Tool | Описание |
|------|----------|
| `list_tags` | Список тегов |
| `create_tag` | Создать тег |
| `update_tag` | Обновить тег |
| `delete_tag` | Удалить тег |

### Custom Fields (4)
| Tool | Описание |
|------|----------|
| `list_custom_fields` | Список пользовательских полей |
| `create_custom_field` | Создать поле |
| `update_custom_field` | Обновить поле |
| `delete_custom_field` | Удалить поле |

### Currencies (1)
| Tool | Описание |
|------|----------|
| `list_currencies` | Список валют |

### Projects (5)
| Tool | Описание |
|------|----------|
| `list_projects` | Список проектов |
| `get_project_by_id` | Получить проект |
| `create_project` | Создать проект |
| `update_project` | Обновить проект |
| `delete_project` | Удалить проект |

### Portfolio (4)
| Tool | Описание |
|------|----------|
| `list_portfolio` | Список портфелей |
| `create_portfolio` | Создать портфель |
| `update_portfolio` | Обновить портфель |
| `delete_portfolio` | Удалить портфель |

### Boards (5)
| Tool | Описание |
|------|----------|
| `list_boards` | Список досок |
| `get_board_by_id` | Получить доску |
| `create_board` | Создать доску |
| `update_board` | Обновить доску |
| `delete_board` | Удалить доску |

### Board Columns (5)
| Tool | Описание |
|------|----------|
| `list_board_columns` | Список столбцов |
| `get_board_column_by_id` | Получить столбец |
| `create_board_column` | Создать столбец |
| `update_board_column` | Обновить столбец |
| `delete_board_column` | Удалить столбец |

### Tasks (7) ⭐
| Tool | Описание |
|------|----------|
| `list_tasks` | Список задач с фильтрацией |
| `get_task_by_id` | Получить задачу |
| `create_task` | Создать задачу |
| `update_task` | Обновить задачу |
| `delete_task` | Удалить задачу |
| `search_task_in_project` | Поиск в проекте |
| `search_task_global` | Глобальный поиск |

### Funnels (5)
| Tool | Описание |
|------|----------|
| `list_funnels` | Список воронок |
| `get_funnel_by_id` | Получить воронку |
| `create_funnel` | Создать воронку |
| `update_funnel` | Обновить воронку |
| `delete_funnel` | Удалить воронку |

### Funnel Statuses (5)
| Tool | Описание |
|------|----------|
| `list_funnel_statuses` | Список статусов |
| `get_funnel_status_by_id` | Получить статус |
| `create_funnel_status` | Создать статус |
| `update_funnel_status` | Обновить статус |
| `delete_funnel_status` | Удалить статус |

### Deals (5)
| Tool | Описание |
|------|----------|
| `list_deals` | Список сделок |
| `get_deal_by_id` | Получить сделку |
| `create_deal` | Создать сделку |
| `update_deal` | Обновить сделку |
| `delete_deal` | Удалить сделку |

### Organizations (5)
| Tool | Описание |
|------|----------|
| `list_organizations` | Список организаций |
| `get_organization_by_id` | Получить организацию |
| `create_organization` | Создать организацию |
| `update_organization` | Обновить организацию |
| `delete_organization` | Удалить организацию |

### Contacts (5)
| Tool | Описание |
|------|----------|
| `list_contacts` | Список контактов |
| `get_contact_by_id` | Получить контакт |
| `create_contact` | Создать контакт |
| `update_contact` | Обновить контакт |
| `delete_contact` | Удалить контакт |

### Attachments (3)
| Tool | Описание |
|------|----------|
| `get_attachment` | Получить вложение |
| `upload_attachment` | Загрузить файл |
| `delete_attachment` | Удалить вложение |

### Tag Extras (2)
| Tool | Описание |
|------|----------|
| `get_tag_details` | Детали тега |
| `get_tasks_by_tag` | Задачи по тегу |

---

## 💡 Примеры использования

### Создание задачи с приоритетом

```python
# Через MCP клиент
result = await mcp_client.call("create_task", {
    "title": "Implement user authentication",
    "project_id": "proj_abc",
    "description": "Add OAuth2 integration",
    "priority": "high",
    "due_date": "2025-12-31",
    "assigned_to": "user_123",
    "tags": ["backend", "security"]
})
```

### Поиск задач

```python
# Найти высокоприоритетные открытые задачи
tasks = await mcp_client.call("list_tasks", {
    "project_id": "proj_abc",
    "status": "open",
    "priority": "high",
    "search": "bug",
    "limit": 10
})
```

### Управление сделками

```python
# Создать сделку
deal = await mcp_client.call("create_deal", {
    "title": "Enterprise License",
    "funnel_id": "funnel_123",
    "status_id": "status_new",
    "amount": 50000,
    "currency": "USD",
    "contact_id": "contact_456"
})

# Переместить сделку в другой статус
await mcp_client.call("update_deal", {
    "deal_id": deal["id"],
    "status_id": "status_won"
})
```

### Работа с контактами

```python
# Создать контакт
contact = await mcp_client.call("create_contact", {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "organization_id": "org_123"
})

# Получить контакты организации
contacts = await mcp_client.call("list_contacts", {
    "organization_id": "org_123",
    "limit": 20
})
```

---

## 🧪 Тестирование

### Запуск интеграционных тестов

```bash
# Установить токен и запустить тесты
WEEEK_TOKEN="your-token" python tests/test_integration.py
```

### Чеклист тестирования

- [x] Workspace info
- [x] User operations
- [x] Project CRUD
- [x] Task CRUD
- [x] Tag operations
- [x] Board operations
- [x] Funnel & Deal operations
- [x] Contact & Organization operations
- [x] Error handling (401, 404, 429)

---

## 🔒 Безопасность

- ✅ Токены **никогда не логируются** (автоматическая редакция)
- ✅ Все данные передаются через **HTTPS**
- ✅ Поддержка переменных окружения для секретов
- ✅ Валидация всех входных данных

---

## 📁 Структура проекта

```
weeek-mcp-server/
├── README.md                 # Документация
├── requirements.txt          # Зависимости
├── env.example               # Пример конфигурации
├── .env                      # Локальная конфигурация (не в git)
├── .gitignore
├── Dockerfile                # Docker образ
├── docker-compose.yml        # Docker Compose конфигурация
├── .dockerignore             # Исключения для Docker
├── run_server.py             # Скрипт запуска
├── src/
│   ├── __init__.py
│   ├── server.py             # MCP сервер
│   ├── weeek_client.py       # HTTP клиент
│   ├── config.py             # Конфигурация
│   ├── tools/                # Все MCP инструменты
│   │   ├── workspace_tools.py
│   │   ├── user_tools.py
│   │   ├── tag_tools.py
│   │   ├── task_tools.py
│   │   └── ...
│   ├── schemas/
│   │   └── models.py         # Pydantic модели
│   └── utils/
│       ├── errors.py         # Обработка ошибок
│       └── logger.py         # Логирование
└── tests/
    └── test_integration.py   # Интеграционные тесты
```

---

## 🐛 Обработка ошибок

Сервер обрабатывает все типы ошибок Weeek API:

| HTTP код | Ошибка | Описание |
|----------|--------|----------|
| 400 | `WeeekValidationError` | Неверные параметры запроса |
| 401 | `WeeekAuthError` | Проблема с токеном |
| 403 | `WeeekForbiddenError` | Нет прав доступа |
| 404 | `WeeekNotFoundError` | Ресурс не найден |
| 429 | `WeeekRateLimitError` | Превышен лимит запросов |
| 5xx | `WeeekServerError` | Ошибка сервера Weeek |

---

## 🤝 Contributing

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing`)
5. Откройте Pull Request

---

## 📄 License

MIT License - см. [LICENSE](LICENSE) файл.

---

## 📞 Поддержка

- **Weeek API Documentation:** https://developers.weeek.net/api/
- **MCP Specification:** https://modelcontextprotocol.io/
- **Issues:** [GitHub Issues](https://github.com/your-repo/weeek-mcp-server/issues)

---

**Made with ❤️ for the Weeek community**

