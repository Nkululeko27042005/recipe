# RecipE 📖

> A book-themed recipe sharing platform built with Flask — discover, write, like, save, and share recipes with a community of cooks.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the App](#running-the-app)
  - [Database Migrations](#database-migrations)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Dashboard Sections](#dashboard-sections)
- [File Uploads](#file-uploads)
- [Configuration](#configuration)
- [Contributing](#contributing)

---

## Overview

**RecipE** is a full-stack web application that lets users write and publish recipes, interact with other cooks through likes, comments, and follows, and discover content through a rich, personalised dashboard. The UI uses a warm book/bookshelf aesthetic with hand-crafted CSS — no external UI frameworks.

---

## Features

### Recipes
- Create, edit, and delete recipes with a rich form
- Attach multiple **images** and an optional **video**
- Structured **ingredients** (name, quantity, unit, weight, notes) and numbered **steps**
- Browse & search recipes by title or category with pagination
- **Save** recipes to a personal cookbook

### Users & Social
- Register / login with hashed passwords (bcrypt)
- Upload and update a **profile picture**
- Write a **bio** and set food preferences (categories & dietary)
- **Follow / unfollow** other cooks
- View any user's public profile with their recipe list and stats

### Interactions
- **Like / Dislike** recipes (one reaction per user, toggleable)
- **Comment** on recipes with nested reply support
- **Save** recipes to revisit later

### Discovery Dashboard
| Section | Description |
|---|---|
| 🏆 All-Time Legend | Single most famous recipe (weighted: likes ×3, saves ×2, comments ×1) |
| 🔥 Recipe of the Month | Most interacted recipe since the 1st of the current month |
| Recommended For You | Personalised by preferences + followed cooks |
| Your Recipes | Your own published recipes |
| Saved | Your bookmarked recipes |
| The Main Shelf | Latest recipes from all cooks |
| ✨ Fresh This Week | Recipes published in the last 7 days |
| Top Liked | All-time most liked recipes (≥1 like required) |
| 🔖 Most Saved | Recipes bookmarked by the most users |
| 📅 This Month's Top Cooks | Ranked podium by interaction score (likes ×3, comments ×2, saves ×1) |
| 📈 Rising Cooks | Cooks who gained the most followers in the last 30 days |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask 3 |
| **ORM** | Flask-SQLAlchemy + Flask-Migrate (Alembic) |
| **Auth** | Flask-Login + Flask-Bcrypt |
| **Database** | SQLite (dev) — swappable via `DATABASE_URL` |
| **Templates** | Jinja2 |
| **Frontend** | Vanilla JS (no frameworks), custom CSS |
| **Fonts** | Playfair Display + Crimson Text (Google Fonts) |
| **File storage** | Local filesystem (`app/static/uploads/`) |

---

## Project Structure

```
recipe/
├── run.py                   # Entry point
├── config.py                # Configuration class
├── requirements.txt
├── .env                     # Local environment variables (not committed)
│
└── app/
    ├── __init__.py          # Application factory
    ├── extensions.py        # db, migrate, login_manager, bcrypt
    │
    ├── models/
    │   ├── user.py          # User, UserPreference
    │   ├── recipe.py        # Recipe, saved_recipes (M2M)
    │   ├── ingredient.py    # Ingredient
    │   ├── step.py          # Step
    │   ├── image.py         # RecipeImage
    │   ├── video.py         # RecipeVideo
    │   ├── comment.py       # Comment (threaded)
    │   ├── reaction.py      # Reaction (like/dislike)
    │   └── follow.py        # Follow
    │
    ├── routes/
    │   ├── auth.py          # /auth  — register, login, logout, /me
    │   ├── users.py         # /users — profile, settings, update, search
    │   ├── recipes.py       # /recipes — CRUD, save/unsave, browse
    │   ├── comments.py      # /comments — list, add, delete
    │   ├── reactions.py     # /reactions — like, dislike
    │   ├── follows.py       # /follows — follow, unfollow, followers, following
    │   └── feed.py          # / — dashboard + JSON API endpoints
    │
    ├── services/
    │   ├── user_service.py
    │   ├── recipe_service.py
    │   ├── comment_service.py
    │   ├── reaction_service.py
    │   ├── follow_service.py
    │   └── feed_service.py  # All ranking & discovery queries
    │
    ├── utils/
    │   ├── file_handler.py  # save_file / delete_file
    │   ├── decorators.py    # login_required_json
    │   └── responses.py     # ok / created / error helpers
    │
    ├── templates/
    │   ├── base.html
    │   ├── dashboard.html
    │   ├── profile.html
    │   ├── settings.html
    │   ├── recipe_form.html
    │   ├── recipe_detail.html
    │   ├── recipe_list.html
    │   ├── login.html
    │   ├── register.html
    │   └── partials/
    │       └── _recipe_card.html
    │
    └── static/
        ├── css/style.css
        ├── js/main.js
        └── uploads/         # User-uploaded images & videos
```

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- `pip`
- (Optional) `virtualenv` or any virtual environment manager

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/recipe.git
cd recipe

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy the example below into a `.env` file at the project root:

```ini
FLASK_APP=run.py
FLASK_ENV=development

# Change this to a long random string in production
SECRET_KEY=change-me-in-production

# SQLite (default). Replace with a Postgres URL for production:
# DATABASE_URL=postgresql://user:password@localhost/recipe
DATABASE_URL=sqlite:///recipe.db

# Where uploaded images and videos are stored
UPLOAD_FOLDER=app/static/uploads
```

> **Never commit your `.env` file.** Add it to `.gitignore`.

### Running the App

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000`.

On first run, `db.create_all()` is called automatically, so the SQLite database and all tables are created for you.

### Database Migrations

If you modify any models, use Flask-Migrate to manage schema changes:

```bash
# Initialise (first time only)
flask db init

# Generate a migration
flask db migrate -m "describe your change"

# Apply the migration
flask db upgrade
```

---

## Usage

### Registering & Logging In

1. Visit `/auth/register` and create an account.
2. Optionally set food **preferences** (categories and dietary requirements) in **Settings**.
3. Upload a **profile picture** from the Settings page.

### Creating a Recipe

1. Click **+ New Recipe** in the navigation bar.
2. Fill in the title, description, and category.
3. Add **ingredients** (with quantity, unit, weight, and notes) and **steps** using the dynamic list builder.
4. Attach one or more **photos** and an optional **video**.
5. Submit — your recipe appears immediately on the shelf.

### Interacting with Recipes

| Action | How |
|---|---|
| ♥ Like | Click the heart button on any recipe card or detail page |
| ✖ Dislike | Click the X button |
| 🔖 Save | Click "Save to my cookbook" |
| 💬 Comment | Use the comment form on the recipe detail page; reply to any comment |
| 👤 Follow a cook | Visit their profile and click **Follow** |

---

## API Reference

All JSON endpoints return `{ "success": true/false, "data": ..., "message": "..." }`.

### Auth — `/auth`

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in |
| `POST` | `/auth/logout` | Log out |
| `GET` | `/auth/me` | Current user info |

### Users — `/users`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/users/<id>` | — | Get a user by ID |
| `PUT` | `/users/me` | ✓ | Update bio and/or profile picture (multipart) |
| `GET` | `/users/me/preferences` | ✓ | Get preferences |
| `PUT` | `/users/me/preferences` | ✓ | Update preferences |
| `GET` | `/users/search?q=` | — | Search users by username |

### Recipes — `/recipes`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/recipes/` | — | List recipes (JSON, supports `?category=`, `?q=`, `?limit=`, `?offset=`) |
| `GET` | `/recipes/<id>` | — | Get a single recipe (JSON, detailed) |
| `POST` | `/recipes/` | ✓ | Create a recipe (JSON or multipart) |
| `PUT` | `/recipes/<id>` | ✓ | Update a recipe |
| `DELETE` | `/recipes/<id>` | ✓ | Delete a recipe |
| `POST` | `/recipes/<id>/save` | ✓ | Save a recipe |
| `DELETE` | `/recipes/<id>/save` | ✓ | Unsave a recipe |

### Comments — `/comments`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/comments/recipe/<id>` | — | List comments for a recipe |
| `POST` | `/comments/recipe/<id>` | ✓ | Add a comment (supports `parent_id` for replies) |
| `DELETE` | `/comments/<id>` | ✓ | Delete own comment |

### Reactions — `/reactions`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/reactions/<recipe_id>/like` | ✓ | Like a recipe |
| `POST` | `/reactions/<recipe_id>/dislike` | ✓ | Dislike a recipe |

### Follows — `/follows`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/follows/<user_id>` | ✓ | Follow a user |
| `DELETE` | `/follows/<user_id>` | ✓ | Unfollow a user |
| `GET` | `/follows/<user_id>/followers` | — | List a user's followers |
| `GET` | `/follows/<user_id>/following` | — | List who a user follows |

### Feed / Dashboard — `/api`

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/feed` | Latest recipes |
| `GET` | `/api/top-liked` | Top liked recipes |
| `GET` | `/api/most-saved` | Most bookmarked recipes |
| `GET` | `/api/fresh-this-week` | Recipes from the last 7 days |
| `GET` | `/api/rising-users` | Cooks rising in the last 30 days |
| `GET` | `/api/top-cooks-this-month` | This month's highest-scoring cooks |
| `GET` | `/api/recommended` | Personalised recommendations (auth) |
| `GET` | `/api/my-recipes` | Your own recipes (auth) |
| `GET` | `/api/saved` | Your saved recipes (auth) |

---

## Dashboard Sections

The dashboard uses several **ranking algorithms** powered by weighted interaction scores:

### Rising Cooks
Users who gained the most **new followers in the last 30 days** — not simply those with the most followers overall. This surfaces momentum, not just popularity.

### This Month's Top Cooks
Weighted score across all recipes published by that cook, counting only interactions that happened this month:
```
score = (likes × 3) + (comments × 2) + (saves × 1)
```

### Most Famous Recipe (All-Time Legend)
The single highest-scoring recipe across all time:
```
score = (likes × 3) + (saves × 2) + (comments × 1)
```

### Recipe of the Month
The recipe with the most total interactions (likes + comments + saves) since the first of the current calendar month.

---

## File Uploads

- **Images**: PNG, JPG, JPEG, GIF, WEBP — max 100 MB per request (default Flask limit)
- **Videos**: MP4, WEBM, MOV
- Files are stored locally in `app/static/uploads/` with a UUID prefix to avoid name collisions
- Old profile pictures and recipe images are **deleted from disk** when replaced or removed

For production, consider replacing local storage with an object store (AWS S3, Cloudflare R2, etc.) and updating `save_file` / `delete_file` in [`app/utils/file_handler.py`](app/utils/file_handler.py).

---

## Configuration

All settings live in [`config.py`](config.py) and can be overridden via `.env`:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret` | Flask session secret — **change in production** |
| `DATABASE_URL` | `sqlite:///recipe.db` | SQLAlchemy database URI |
| `UPLOAD_FOLDER` | `app/static/uploads` | Path for uploaded files |
| `MAX_CONTENT_LENGTH` | `100 MB` | Maximum upload size |
| `ALLOWED_IMAGE_EXT` | `png, jpg, jpeg, gif, webp` | Accepted image formats |
| `ALLOWED_VIDEO_EXT` | `mp4, webm, mov` | Accepted video formats |

---

## Contributing

1. Fork the repository and create a feature branch.
2. Keep business logic in `services/`, HTTP concerns in `routes/`.
3. Use `flask db migrate` for any model changes.
4. Test file uploads manually — the test suite is not yet included.
5. Open a pull request with a clear description of the change.
