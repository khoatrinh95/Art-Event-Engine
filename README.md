# Art Event Engine

> Work in progress. The long-term goal is to develop a fully functional web app that allows users to look up upcoming art events happening in their city.

## Project Overview

Art Event Engine is a Python project for discovering art event opportunities and calls for artists in a local area. It currently uses search and extraction logic to gather candidate event pages, fetch page content, and identify calls for artists or vendors.

## Current Status

- CLI-based prototype built around `art_event_engine.py`
- Uses search query aggregation and page analysis
- Extracts event data and saves results to JSON
- Not yet a web application
- Work in progress toward a city-focused event lookup web app

## What it does today

- searches for candidate event pages using configured queries
- fetches and analyzes page or social snippet text
- filters for active calls for artists/vendors
- prints event summaries to the console
- saves results to `events_<location>_<timestamp>.json`

## Requirements

- Python 3.11+ (or compatible Python 3.x)
- `pip install -r requirements.txt`
- API keys for:
  - `TAVILY_API_KEY`
  - `ANTHROPIC_API_KEY`

## Setup

1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with:

```env
TAVILY_API_KEY="your_tavily_api_key"
ANTHROPIC_API_KEY="your_anthropic_api_key"
```

## Usage

Run the engine from the repository root:

```bash
python art_event_engine.py
```

If required keys are missing, the script will prompt for them.

## Configuration

Key settings live in `event_engine/config.py`, including:

- `LOCATION` — current city scope (default: Montreal)
- search query templates
- minimum confidence threshold
- blocked domains
- fetch delay and page size limits

## Project Structure

- `art_event_engine.py` — main CLI entrypoint
- `event_engine/` — core extraction, fetching, filtering, and display logic
- `tests/` — unit tests
- `.gitignore` — ignored files and local artifacts
- `requirements.txt` — Python dependencies

## Running Tests

```bash
pytest
```

## Future Goals

- full web app interface for city-based event discovery
- user search and filter experience
- event details, location, and date display
- persistent storage and favorite/save functionality
- deployment to a web hosting platform

## Notes

This repository is currently a prototype proof of concept. The focus is on converting search and extraction logic into a user-friendly web application for discovering art events in a city.
