# Kadman — Vendor Management System

A full-stack web application for managing market vendors. Supports layout planning, attendance tracking, payment verification via PromptPay slip scanning, and LINE OA notifications.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, TypeScript, Vite, Tailwind CSS |
| Backend | Python 3.9, Flask |
| Database | MySQL 8 |
| Search | Elasticsearch 8 |
| Notifications | LINE Messaging API |
| Payment Verification | EasySlip API + AWS S3 |
| Tunnel (local dev) | ngrok |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Node.js](https://nodejs.org/) (v18+)
- A [LINE Developer account](https://developers.line.biz/) with a Messaging API channel
- An [ngrok account](https://ngrok.com/) (free tier works)

---

## First-Time Setup

### 1. Start infrastructure (Docker)

```bash
# MySQL
docker run -d --name kadman-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=kadman1234 \
  -e MYSQL_DATABASE=kadman \
  mysql:8.0

# Elasticsearch (port 9300 because Windows reserves 9200 via Hyper-V)
docker run -d --name elasticsearch \
  -p 9300:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
```

### 2. Create the database tables

Wait ~20 seconds for MySQL to start, then:

```bash
docker exec -i kadman-mysql mysql -u root -pkadman1234 kadman <<'SQL'
CREATE TABLE vendors (
    vendorID        INT AUTO_INCREMENT PRIMARY KEY,
    shop_name       VARCHAR(255),
    badges          TEXT,
    lineID          VARCHAR(100),
    attendance      INT DEFAULT 3,
    attendance_days TEXT,
    payment         VARCHAR(100)
);
CREATE TABLE layouts (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(255),
    data    LONGTEXT,
    status  VARCHAR(50) DEFAULT 'inactive'
);
CREATE TABLE waiting_vendors (
    LineID       VARCHAR(100) PRIMARY KEY,
    UserProfile  VARCHAR(255)
);
CREATE TABLE SlipHistory (
    SlipHistory_id   INT AUTO_INCREMENT PRIMARY KEY,
    SlipHistory_ref  VARCHAR(255) UNIQUE
);
SQL
```

### 3. Set up the Python environment

```bash
conda create --name kadman python=3.9 -y
conda activate kadman
pip install flask flask-cors mysql-connector-python python-dotenv \
            requests elasticsearch==8.13.0 pythainlp boto3
```

### 4. Configure environment variables

Copy and fill in `server/.env`:

```env
# Frontend URL (update to your ngrok URL when using LINE notifications)
FRONTEND_URL=http://localhost:5173

# MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=kadman1234
MYSQL_DB=kadman
MYSQL_PORT=3306

# LINE Official Account — Channel Access Token from LINE Developers Console
LineOA_Key=your_line_channel_access_token_here

# Elasticsearch
ELASTIC_URL=http://localhost:9300

# EasySlip API (only needed for payment slip verification)
EASY_SLIP_KEY=your_easyslip_token_here
```

### 5. Index vendor data into Elasticsearch

```bash
conda activate kadman
cd server
python scripts/indexing.py
```

### 6. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the App

Open **3 terminals**:

**Terminal 1 — Backend**
```bash
conda activate kadman
cd server
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

**Terminal 3 — ngrok** (only needed for LINE webhook / notifications)
```bash
cd server
./ngrok http 5000
# Copy the HTTPS URL and set it as the Webhook URL in LINE Developers Console
# Also update FRONTEND_URL in server/.env to your ngrok frontend tunnel
```

---

## LINE Webhook Setup

1. Run ngrok: `./ngrok http 5000`
2. Copy the public HTTPS URL (e.g. `https://xxxx.ngrok-free.app`)
3. Go to [LINE Developers Console](https://developers.line.biz) → your channel → **Messaging API**
4. Set **Webhook URL** to `https://xxxx.ngrok-free.app/webhook`
5. Enable **Use webhook**
6. Update `FRONTEND_URL` in `server/.env` to the ngrok URL pointing at your frontend

> ngrok's free tier generates a new URL on every restart — update the webhook URL each time.

---

## Daily Startup (after first-time setup)

```bash
docker start kadman-mysql elasticsearch
conda activate kadman && cd server && python app.py   # terminal 1
cd frontend && npm run dev                             # terminal 2
```

---

## API Endpoints

### Layouts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/show_all_layouts` | Get all layouts |
| POST | `/insert_layout` | Create a new layout |
| PUT | `/update_layout/<id>` | Update a layout |
| DELETE | `/delete_layout/<id>` | Delete a layout |
| GET | `/begin_attendance/<id>` | Start attendance check, notifies vendors via LINE |
| GET | `/get_all_active_layout` | Get layouts with status `active` |
| PUT | `/reset_all_attendance` | Reset all layouts to inactive |

### Vendors
| Method | Endpoint | Description |
|---|---|---|
| GET | `/get_all_vendors` | Get all vendors |
| POST | `/add_vendors` | Add a new vendor |
| POST | `/update_badges` | Update vendor badges |
| POST | `/delete_selected_badges` | Remove specific badges from a vendor |
| POST | `/check_attendance/<layout_id>` | Record attendance and send payment link |
| POST | `/get_quota` | Get remaining attendance quota for a LINE user |
| GET | `/get_payment/<vendorID>` | Get payment status for a vendor |
| POST | `/increase_attendance` | Increment attendance count |
| POST | `/decrease_attendance` | Decrement attendance count |
| POST | `/reset_attendance` | Reset all attendance to 3 |
| GET | `/search?q=<query>` | Search vendors (Thai + English) |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload and verify a PromptPay payment slip |

### Webhook
| Method | Endpoint | Description |
|---|---|---|
| POST | `/webhook` | LINE webhook — registers new followers as waiting vendors |

---

## Project Structure

```
Kadman/
├── frontend/               # Vue 3 + TypeScript (Vite)
│   ├── src/
│   │   ├── views/          # Page components
│   │   ├── components/     # Reusable UI components
│   │   ├── services/       # API call wrappers
│   │   └── router/         # Vue Router config
│   └── .env                # VITE_API_BASE_URL
├── server/                 # Flask backend
│   ├── app.py              # App factory, blueprint registration
│   ├── db.py               # MySQL connection helper
│   ├── routes/             # Flask blueprints
│   │   ├── layouts.py      # Layout routes + LINE helpers
│   │   ├── vendors.py      # Vendor routes + Elasticsearch search
│   │   ├── verification.py # Payment slip upload + EasySlip verification
│   │   └── webhook.py      # LINE webhook handler
│   ├── utils/
│   │   └── vendor_tools.py # Shared business logic
│   ├── data/
│   │   └── vendors.json    # Vendor seed data (111 vendors)
│   ├── scripts/
│   │   └── indexing.py     # One-time Elasticsearch indexing script
│   ├── tests/              # Pytest test suites
│   ├── public/             # Static HTML for LINE OA pages
│   ├── static/             # QR code images
│   ├── ngrok.exe           # ngrok tunnel binary
│   └── .env                # Backend environment variables
├── LineOA/                 # LINE OA test utilities
└── README.md
```
