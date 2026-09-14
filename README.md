# 🌾 TerraLens

**TerraLens** is a simple, farmer-friendly web app to help farmers manage their fields (*khet*) — track crops, seasons, soil type, and keep a photo diary of each field's progress over time, complete with real weather data.

Built with a focus on accessibility: fully available in **Hindi, English, and Hinglish (Hindi + English)**, so farmers can use it in whichever language feels most natural.

---

## ✨ Features

- **Field Management** — Add, view, and delete fields with details like crop, season, area, village/district, GPS location, and soil type
- **Khet ki Diary** — Add dated photo updates with optional notes for each field, deletable individually
- **Real Weather** — Every diary update automatically fetches real weather (temperature + conditions) for the field's location using [Open-Meteo](https://open-meteo.com/) (free, no API key required)
- **Multi-language Support** — Full UI translation across Hindi, English, and Hinglish, switchable anytime via the language toggle
- **Photo Storage** — Field and diary photos are uploaded to [Cloudinary](https://cloudinary.com/) for permanent, reliable hosting
- **GPS Auto-fill** — One-tap location capture using the browser's Geolocation API
- **Per-device Identity** — Each device gets a private, anonymous ID so a farmer's data stays their own, without requiring login/signup

---

## 🛠 Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) (Python)
- [MongoDB Atlas](https://www.mongodb.com/atlas) — database
- [Cloudinary](https://cloudinary.com/) — image storage
- [Open-Meteo API](https://open-meteo.com/) — weather data
- Hosted on [Render](https://render.com/)

**Frontend**
- Plain HTML/CSS/JavaScript (no framework)
- [Tailwind CSS](https://tailwindcss.com/) (via CDN)
- Hosted as a static site on [Render](https://render.com/)

---

## 📁 Project Structure

```
Terralens/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes
│   │   ├── models.py        # Pydantic data models
│   │   ├── db.py            # MongoDB connection
│   │   └── config.py        # App configuration
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── stitch_home.html     # Home screen
    ├── my_fields.html       # Field list
    ├── add_field.html       # Add new field form
    ├── field_detail.html    # Field detail + diary
    ├── language_select.html # Onboarding language picker
    └── translations.js      # i18n strings (Hindi/English/Hinglish)
```

---

## 🚀 Setup

### Backend

1. Navigate to the `backend/` folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your values:
   ```
   MONGODB_URI=<your MongoDB Atlas connection string>
   MONGODB_DATABASE=terralens
   CLOUDINARY_CLOUD_NAME=<your Cloudinary cloud name>
   CLOUDINARY_API_KEY=<your Cloudinary API key>
   CLOUDINARY_API_SECRET=<your Cloudinary API secret>
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. API docs available at `http://localhost:8000/docs`

### Frontend

The frontend is static HTML/CSS/JS — no build step required. Just update the `API_BASE` constant in each HTML file to point at your backend URL, then serve the `frontend/` folder with any static host (or open directly in a browser for local testing).

---

## 🔑 Environment Variables (Backend)

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | Database name (e.g. `terralens`) |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

**Important:** In MongoDB Atlas, make sure **Network Access** allows connections from `0.0.0.0/0` (or your host's specific IPs) — otherwise the backend will fail to connect.

---

## 📡 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/fields` | List all fields (optionally filtered by `user_id`) |
| `POST` | `/fields` | Create a new field |
| `GET` | `/fields/{id}` | Get a single field |
| `DELETE` | `/fields/{id}` | Delete a field |
| `POST` | `/fields/{id}/photo` | Upload/update a field's photo |
| `GET` | `/fields/{id}/updates` | List diary updates for a field |
| `POST` | `/fields/{id}/updates` | Add a new diary update (photo + note) |
| `DELETE` | `/fields/{id}/updates/{update_id}` | Delete a diary update |
| `GET` | `/updates/recent` | Get recent diary updates across all fields |
| `GET` / `POST` | `/user` | Get/save user profile (name, language) |

Full interactive API docs available at `/docs` once the backend is running.

---

## 🌍 Localization

All user-facing text lives in `frontend/translations.js`, organized by language (`hinglish`, `hindi`, `english`). Every page calls `applyTranslations()` on load, and the selected language persists across the app via `localStorage`.

To add a new translatable string:
1. Add the key to all three language objects in `translations.js`
2. Use `data-i18n="yourKey"` on the element (or `data-i18n-placeholder` for input placeholders)

---

## 📄 License

This project is currently unlicensed — add a license of your choice before public release.
