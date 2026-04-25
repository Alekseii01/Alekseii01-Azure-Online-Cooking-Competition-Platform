# Azure Online Cooking Competition Platform

## Services

| Service | Port | Schema | Tables |
|---|---|---|---|
| UserService | 8000 | `user_service` | users |
| CompetitionService | 8001 | `competition_service` | competitions, entries |
| RecipeService | 8002 | `recipe_service` | categories, recipes, ingredients |
| FeedbackService | 8003 | `feedback_service` | feedback, ratings |

## API Endpoints

**UserService** `http://127.0.0.1:8000`
- `GET /health`
- `GET /users`
- `GET /users/{user_id}`

**CompetitionService** `http://127.0.0.1:8001`
- `GET /health`
- `GET /competitions`
- `GET /competitions/{competition_id}`
- `GET /entries`
- `GET /competitions/{competition_id}/entries`

**RecipeService** `http://127.0.0.1:8002`
- `GET /health`
- `GET /categories`
- `GET /recipes` — query params: `category_id`, `search`
- `GET /recipes/{recipe_id}` — includes ingredients
- `GET /ingredients`

**FeedbackService** `http://127.0.0.1:8003`
- `GET /health`
- `GET /feedback` — query param: `entry_id`
- `GET /ratings` — query param: `entry_id`

## Messaging

`CompetitionService` publishes a message to an Azure Service Bus queue every time
`GET /competitions/{competition_id}/entries` is called:

```json
{"event": "entries_viewed", "competition_id": 1, "entry_count": 2}
```

`FeedbackService` runs a background worker (started on app startup) that polls the
same queue every 10 seconds, logs each received message, and completes it.

The shared helper [`common/message_bus.py`](common/message_bus.py) exposes
`publish_message()` and `receive_messages()` used by both services.

## Environment

Create a `.env` file in the project root (see `.env.example`):

```env
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_SERVER=tcp:your_server.database.windows.net
DB_DATABASE=your_database
SB_SEND_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=send;SharedAccessKey=<key>;EntityPath=<queue>
SB_LISTEN_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=listen;SharedAccessKey=<key>;EntityPath=<queue>
```

The Azure SQL firewall must allow your client IP. Add it in Azure Portal → SQL server → Networking.

## Local Run

```bash
python3 -m venv .venv
CFLAGS="-I$(brew --prefix unixodbc)/include" LDFLAGS="-L$(brew --prefix unixodbc)/lib" .venv/bin/pip install pyodbc
.venv/bin/pip install fastapi uvicorn sqlalchemy python-dotenv
```

Initialize schemas, tables, and stub data:

```bash
.venv/bin/python -m sql.init_db
```

Start each service in a separate terminal:

```bash
.venv/bin/python -m uvicorn user_service.app:app --host 127.0.0.1 --port 8000
.venv/bin/python -m uvicorn competition_service.app:app --host 127.0.0.1 --port 8001
.venv/bin/python -m uvicorn recipe_service.app:app --host 127.0.0.1 --port 8002
.venv/bin/python -m uvicorn feedback_service.app:app --host 127.0.0.1 --port 8003
```

## Docker Run

Build and initialize:

```bash
docker compose build
docker compose run --rm db-init
```

Start all services:

```bash
docker compose up -d user-service competition-service recipe-service feedback-service
```

Stop:

```bash
docker compose down
```
