��# CLAUDE.md — Day Tripping Road Trip Map App

> **Read this file before every session. Update it as the project evolves.**
> This is the single source of truth for architecture, decisions, and status.

## Project Overview

**Day Tripping** is a market-ready, publicly distributable macOS road trip planner that combines an interactive Leaflet.js map, intelligent route planning, location discovery with rich media (photos, facts, restaurants, weather), and offline resilience — all in one native application.

This is not a personal project — it is intended for public release. Every interaction, animation, and data flow must feel polished enough that a stranger would pay for it.

## The Problem

Planning a road trip requires bouncing between Google Maps, Yelp, TripAdvisor, blogs, and spreadsheets. None give a single, beautiful, offline-capable experience to visualize an entire journey, discover stops, and keep everything in one place.

## Core Roles

1. **Route Planner** — fast, intuitive route planning with multi-route options
2. **Discovery Engine** — surface interesting places with rich photos, facts, activities
3. **Visual Trip Organizer** — full trip at a glance with drag-to-reorder stops
4. **Offline Travel Companion** — everything cached for use without cell service
5. **Trip Archive** — save, manage, revisit, and edit multiple trips

---

## Technical Architecture

### Language & Framework
- **Python 3.11+** (running 3.14.2 on dev machine)
- **customtkinter** — UI framework for home screen ("My Planned Trips")
- **pywebview** — native macOS WebKit window for the interactive map view
- **Folium + Leaflet.js** — map rendering with full interactivity
- **SQLite** — local storage (WAL mode, parameterized queries only)
- **Pillow** — image processing for cached photos and thumbnails
- **requests / httpx** — API calls
- **python-dotenv** — secrets management
- **bcrypt** — developer dashboard password hashing
- **py2app** — macOS `.app` bundle packaging

### Dual-Window Architecture

The app uses two window systems that hand off seamlessly:

1. **Home screen** (`ui/app.py`) — customtkinter `CTk` window
   - Displays "My Planned Trips" grid
   - Theme toggle (Psychedelic / Dark / Light)
   - Trip CRUD operations

2. **Map view** (`ui/map_view.py`) — pywebview WebKit window
   - Loads Folium-generated HTML with Leaflet.js
   - Full map interactivity: pan, zoom, click, markers, polylines
   - Sidebar for itinerary, location details, search
   - Python ↔ JS communication via `pywebview.api` (js_api)

**Transition flow:**
- User clicks a trip on home screen → CTk window hides → pywebview map opens
- User clicks "Home" in map view → pywebview closes → CTk window re-shows

### APIs & Data Sources

All API keys in `.env`. Never hardcoded. Load via `python-dotenv`.

| Service | API | Free Tier | Key In .env |
|---------|-----|-----------|-------------|
| Routing | OpenRouteService | 2,000 req/day | `OPENROUTE_API_KEY` |
| Map Tiles | OpenStreetMap | Unlimited (free) | None needed |
| Satellite Tiles | Mapbox | 50,000 loads/month | `MAPBOX_ACCESS_TOKEN` (optional) |
| Location Photos | Unsplash | 50 req/hour | `UNSPLASH_ACCESS_KEY` |
| Location Photos | Wikimedia Commons | Unlimited | None needed |
| Location Facts | Wikipedia | Unlimited | None needed |
| Restaurants/POI | Google Places (New) | 10,000 Essentials/month | `GOOGLE_PLACES_API_KEY` |
| Restaurants/POI | Foursquare | 10,000 Pro/month | `FOURSQUARE_API_KEY` |
| Weather | OpenWeatherMap | 1,000 calls/day | `OPENWEATHER_API_KEY` |
| Geocoding | Nominatim (OSM) | 1 req/sec | None needed |

**DO NOT use Yelp Fusion API** — no free tier (starts at $7.99/1,000 calls).

**Unsplash Attribution (LEGAL REQUIREMENT):** Every Unsplash photo must display:
"Photo by [Photographer Name] on Unsplash" where photographer name links to their
profile and "Unsplash" links to unsplash.com. All links include UTM params:
`?utm_source=day_tripping&utm_medium=referral`. Store photographer data alongside
cached photos for offline attribution.

### Database Schema

Store DB in `~/Library/Application Support/DayTripping/daytripping.db`
Photo cache in `~/Library/Application Support/DayTripping/photo_cache/`
Tile cache in `~/Library/Application Support/DayTripping/tile_cache/`

```sql
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    start_location TEXT,
    end_location TEXT,
    start_lat REAL,
    start_lng REAL,
    end_lat REAL,
    end_lng REAL,
    route_data TEXT,          -- JSON: selected route + alternatives
    settings TEXT             -- JSON: trip-specific settings
);

CREATE TABLE IF NOT EXISTS stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    stop_type TEXT NOT NULL DEFAULT 'custom',  -- city/landmark/restaurant/custom
    cached_at TEXT
);

CREATE TABLE IF NOT EXISTS stop_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stop_id INTEGER NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
    facts TEXT,               -- JSON array of fact strings
    activities TEXT,           -- JSON array of activity objects
    restaurants TEXT,          -- JSON array of restaurant objects
    weather TEXT,              -- JSON weather data
    fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS stop_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stop_id INTEGER NOT NULL REFERENCES stops(id) ON DELETE CASCADE,
    photo_url TEXT NOT NULL,
    local_path TEXT,
    source TEXT NOT NULL,      -- 'unsplash' / 'wikimedia' / 'pexels'
    photographer_name TEXT,
    photographer_url TEXT,
    attribution_text TEXT,
    cached_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tile_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zoom_level INTEGER NOT NULL,
    tile_x INTEGER NOT NULL,
    tile_y INTEGER NOT NULL,
    tile_data BLOB NOT NULL,
    cached_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(zoom_level, tile_x, tile_y)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_source TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    status_code INTEGER,
    response_time_ms REAL,
    cache_hit INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);
```

**Indexes:**
```sql
CREATE INDEX IF NOT EXISTS idx_stops_trip_id ON stops(trip_id);
CREATE INDEX IF NOT EXISTS idx_stop_details_stop_id ON stop_details(stop_id);
CREATE INDEX IF NOT EXISTS idx_stop_photos_stop_id ON stop_photos(stop_id);
CREATE INDEX IF NOT EXISTS idx_tile_cache_coords ON tile_cache(zoom_level, tile_x, tile_y);
CREATE INDEX IF NOT EXISTS idx_tile_cache_cached_at ON tile_cache(cached_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_source ON api_usage(api_source, timestamp);
```

### Project Structure

```
day-tripping/
├── CLAUDE.md                    — This file (project guide)
├── BUILD.md                     — Build/run instructions
├── .env                         — API keys (NEVER committed)
├── .env.example                 — Template for required keys
├── .gitignore                   — Excludes .env, *.db, caches
├── requirements.txt             — Pinned dependencies
├── setup.py                     — py2app configuration
├── create_icon.py               — Icon PNG → .icns converter
├── run.py                       — Entry point
├── dev_dashboard.py             — Dev-only API monitor (NOT in .app)
├── set_dev_password.py          — One-time bcrypt hash generator (NOT in .app)
├── config/
│   ├── __init__.py
│   ├── settings.py              — App configuration from .env
│   └── themes.py                — Psychedelic/Dark/Light color definitions
├── core/
│   ├── __init__.py
│   ├── api_tracker.py           — Centralized API call logging
│   ├── trip_manager.py          — CRUD for trips and stops
│   ├── route_engine.py          — Route calculation (OpenRouteService)
│   ├── discovery.py             — Smart suggestions engine
│   ├── location_service.py      — Facts, activities, restaurants, weather
│   ├── photo_service.py         — Fetch and cache location photos
│   └── offline_manager.py       — Tile caching, offline detection, sync
├── ui/
│   ├── __init__.py
│   ├── app.py                   — Main CTk application window
│   ├── home_view.py             — "My Planned Trips" screen
│   ├── map_view.py              — Folium + pywebview map controller
│   └── templates/
│       └── map.html             — Leaflet.js map page (loaded in webview)
├── data/
│   ├── __init__.py
│   ├── database.py              — SQLite connection, schema, migrations
│   └── cache.py                 — LRU caching for tiles, photos, API data
├── assets/
│   ├── fonts/                   — Psychedelic display font TTF files
│   └── icon.png                 — App icon (AI-generated)
└── tests/
    ├── __init__.py
    ├── test_database.py
    ├── test_trip_manager.py
    ├── test_route_engine.py
    └── test_cache.py
```

---

## UI/Theme — "Day Tripping" Brand Identity

Rooted in **1960s psychedelic art** — concert posters, VW van culture, tie-dye,
Grateful Dead aesthetic — executed with modern UI polish.

### Three Themes

**Psychedelic (DEFAULT/REDESIGNED):**
- Backgrounds: Deep Indigo (#1A0A2E), Royal Purple (#5B0EA6)
- Primary/Routes: Deep Burnt Orange (#C44B00), Golden Yellow (#F5C400)
- Interactive: Royal Purple (#5B0EA6)
- Discovery: Golden Yellow (#F5C400)
- Text: Warm Cream (#FFF8E7)
- Typography: Boogaloo (Headers), Outfit (Body)
- Aesthetic: Wavy borders, fractal geometry, lava lamp animations

**Dark:**
- Backgrounds: #1a1a2e, #16213e
- Muted versions of psychedelic accents
- Text: #e2e8f0

**Light:**
- Backgrounds: warm cream (#faf5ef), parchment (#f5f0e8)
- Rich accent colors on light base
- Text: #1e293b

### Color Semantics
- **Sunset orange / warm gold** → routes, navigation, primary actions
- **Electric purple** → interactive elements, buttons, selections
- **Teal** → discovery, suggestions, new content
- **Coral pink** → warnings, deletions (replaces harsh red)

### Typography
- **Display font:** Psychedelic TTF (Righteous, Pacifico, or similar from Google Fonts)
- **Body font:** System sans-serif (SF Pro on macOS, or DM Sans / Outfit)

### Psychedelic Effects (tasteful, not overwhelming)
- Gradient meshes as section backgrounds
- Route lines with orange→purple gradient
- Loading animations: lava lamp / gentle swirl (CSS in webview)
- Card hover: subtle shimmer or aurora
- Organic flowing dividers instead of hard borders
- Background textures: paper grain, fabric weave, noise overlays

### What NOT to Do
- Don't make the whole UI look like a blacklight poster
- Keep core interface clean, readable, professional
- User should think "great vibes" not "can't find the button"

---

## App Flow

### Launch Screen — "My Planned Trips" (customtkinter)
- "Day Tripping" in psychedelic display font at top
- Grid/list of saved trip cards: name, start→end, date, mini-map thumbnail
- "＋ New Adventure" button
- Rename, duplicate, delete (with confirmation) via context menu
- Theme toggle: Psychedelic / Dark / Light

### Interactive Map View (pywebview + Leaflet.js)
- Full-screen map centered on US
- Search inputs for start/end points with autocomplete
- Multiple route options (fastest, scenic, shortest) with estimated times/distances
- User selects route → rendered as gradient polyline
- Click or search to add custom stops along route
- Route auto-recalculates with stops
- Collapsible sidebar: ordered itinerary with times and distances

### Location Detail View (in webview)
- Click any stop → detail panel slides in
- **Photos:** Unsplash (with attribution) + Wikimedia Commons, cached locally
- **Facts:** Wikipedia API
- **Activities:** Google Places / Foursquare
- **Weather:** OpenWeatherMap forecast for travel date

### Smart Suggestions
- "Discover" markers near route (national parks, landmarks, restaurants)
- One-click add or dismiss

---

## Offline Functionality

- **Map tiles:** Pre-download corridor tiles (zoom 8-16, 50mi buffer)
- **Route data:** Cached in SQLite
- **Location details:** Cached after first retrieval
- **Offline indicator:** Non-intrusive banner listing limited features
- **Sync on reconnect:** Auto-refresh stale data in background

---

## Developer Dashboard (Separate Program)

**NOT included in .app bundle.** Run via `python3 dev_dashboard.py`.

- Password-protected (bcrypt hash in `DEV_DASHBOARD_PASSWORD_HASH` .env var)
- 3 failed attempts → 15-minute lockout
- Tabs: API Usage, Cost Estimator, Call Log, Cache Stats, Error Log
- Reads from same SQLite `api_usage` table
- Every API call in main app goes through `core/api_tracker.py`

---

## Universal Principles

### 1. Full Codebase Awareness Before Every Change
Read and understand existing files before modifying. Verify the DB schema. Check installed packages. Never guess.

### 2. Professional-Grade UI
Visual polish of a commercial product. Consistent spacing, alignment, typography. Color with purpose. Responsive. Accessible.

### 3. Security-First
- Secrets in `.env`, never hardcoded. `.env.example` with placeholders.
- Parameterized queries only — NEVER string concatenation for SQL.
- Input validation. Path sanitization. No exposed stack traces.
- User data in `~/Library/Application Support/DayTripping/` with owner-only permissions.

### 4. Live Data by Default
Default to reliable free APIs. Cache with timestamps. Serve cached data with stale indicator when offline. Never blank screen or crash.

### 5. Development Workflow
1. Read CLAUDE.md first, every time.
2. Understand current state before changes.
3. Focused, well-commented changes. Docstrings on every function and module.
4. Test after every meaningful change.
5. Explain what was done and why.
6. Ask before architectural decisions.
7. Never break existing functionality.

### 6. Code Quality (Market-Ready)
- Type hints on every function
- `ruff` / `black` formatting
- No TODO/FIXME in shipped code
- DRY — shared utilities for repeated patterns
- Shortest, most efficient code possible

### 7. Performance
- Zero perceptible lag. Background threads for >200ms operations.
- Async API calls — never freeze the UI.
- Lazy loading. LRU eviction for caches.
- Startup under 3 seconds.

### 8. Update CLAUDE.md
Update this file with: completed features, architecture decisions, API quirks, edge cases.

---

## Environment Variables (.env)

```bash
# === Routing ===
OPENROUTE_API_KEY=your-openrouteservice-key

# === Photos ===
UNSPLASH_ACCESS_KEY=your-unsplash-access-key

# === Weather ===
OPENWEATHER_API_KEY=your-openweathermap-key

# === Restaurants & Places ===
GOOGLE_PLACES_API_KEY=your-google-places-key
FOURSQUARE_API_KEY=your-foursquare-key

# === Optional: Satellite Tiles ===
# MAPBOX_ACCESS_TOKEN=your-mapbox-token

# === Developer Dashboard ===
# Run set_dev_password.py to generate hash
DEV_DASHBOARD_PASSWORD_HASH=your-bcrypt-hash-here
```

---

## Build Order

1. ✅ CLAUDE.md
2. ✅ Project structure, .env.example, .gitignore, requirements.txt
3. ✅ Database schema and data layer
4. ✅ API tracker module (before any API calls)
5. ✅ Config modules (settings.py, themes.py)
6. ✅ Home screen with theme toggle
7. ✅ Interactive map view (Folium + pywebview)
8. ✅ Route calculation and rendering
9. ✅ Custom stops and itinerary sidebar
10. ✅ Location detail view (photos, facts, activities, weather)
11. ✅ Smart suggestions engine
12. ✅ Offline caching (tiles, data, detection)
13. ✅ UI polish (animations, gradients, psychedelic effects, fractal backgrounds)
14. ✅ Developer dashboard
15. [ ] py2app packaging and testing

---

## API Quirks & Edge Cases

- OpenRouteService: POST to `/v2/directions/{profile}/geojson` with coordinates array
- Nominatim: rate limit 1 req/sec, MUST include `User-Agent` header
- Unsplash: 50 req/hour on development, 5,000/hour after production approval
- Google Places (New): uses `places.googleapis.com/v1/places:searchNearby` (POST), different from legacy
- Foursquare: Authorization header is just the key (no "Bearer" prefix)
- pywebview on macOS: uses native WebKit via Cocoa, `gui='cocoa'` is default
- pywebview + CTk: run webview in separate thread to avoid blocking CTk mainloop
- Leaflet GeoJSON coordinates are [lng, lat] — reversed from most APIs

---

## Current Status

### Phase 0 — Foundation ✅ COMPLETE
- [x] CLAUDE.md created
- [x] Project scaffolding (all directories, __init__.py files)
- [x] Database layer (data/database.py — 7 tables, WAL mode, indexes)
- [x] API tracker (core/api_tracker.py — async logging)
- [x] Cache module (data/cache.py — LRU eviction, stats)
- [x] Config modules (config/settings.py, config/themes.py)
- [x] Entry point (run.py) and setup.py (py2app)
- [x] .env with API keys from master.env
- [x] .gitignore, .env.example, requirements.txt, BUILD.md
- [x] Git repository initialized

### Phase 1 — Home Screen ✅ COMPLETE
- [x] Main application window (ui/app.py — CTk with theme toggle)
- [x] Three-theme system (Psychedelic/Dark/Light)
- [x] Righteous display font loaded
- [x] Home view (ui/home_view.py — trip cards grid, CRUD)

### Phase 2 — Interactive Map ✅ COMPLETE
- [x] Map view controller (ui/map_view.py — pywebview + Folium)
- [x] Leaflet.js HTML template (ui/templates/map.html)
- [x] Python ↔ JS bridge (MapAPI class with js_api)
- [x] Search with Nominatim autocomplete
- [x] Click-to-add stops

### Phase 3 — Route Calculation ✅ COMPLETE
- [x] Route engine (core/route_engine.py — OpenRouteService)
- [x] Multi-route profiles (fastest, shortest)
- [x] Gradient route rendering (orange→purple)

### Phase 4 — Stops & Itinerary ✅ COMPLETE
- [x] Stop CRUD with reordering
- [x] Itinerary sidebar in webview
- [x] Route recalculation with waypoints

### Phase 5 — Location Details ✅ COMPLETE
- [x] Location service (core/location_service.py)
- [x] Photo service (core/photo_service.py — Unsplash + Wikimedia)
- [x] Wikipedia facts, Google Places activities/restaurants
- [x] OpenWeatherMap weather
- [x] Unsplash attribution (legal compliance)

### Phase 6 — Smart Suggestions ✅ COMPLETE
- [x] Discovery engine (core/discovery.py)
- [x] Route corridor sampling and nearby search

### Phase 7 — Offline Capability ✅ COMPLETE
- [x] Offline manager (core/offline_manager.py)
- [x] Tile pre-download for route corridor
- [x] Connectivity detection
- [x] Stale data sync on reconnect

### Phase 8 — Polish & Packaging (NEXT)
- [x] Developer dashboard (dev_dashboard.py)
- [x] Password setup (set_dev_password.py)
- [x] Icon converter (create_icon.py)
- [x] UI polish (CSS animations, psychedelic effects, fractal backgrounds)
- [ ] py2app build and verification
- [ ] Final testing

## Session Log
- **2026-02-24** — Project created from scratch. All Phase 0-7 modules built and verified. All imports pass on Python 3.14.2. GUI renders with Righteous font and psychedelic theme. Ready for integration testing and UI polish.
� *cascade08��*cascade08��� *cascade08����*cascade08���� *cascade08����*cascade08��Ø *cascade08Øؘ*cascade08ؘ�� *cascade08"(06f4dc7650e0851582b69b2902ce5424d01b3a462-file:///Applications/Day%20Tripping/CLAUDE.md:#file:///Applications/Day%20Tripping