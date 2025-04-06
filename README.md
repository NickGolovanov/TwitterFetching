# Weather Project

## Project Structure

```
.
├── backend/         # API backend API
├── frontend/        # FrontEnd application frontend
└── unigarant_alert_extension/  # Browser extension
```

## Prerequisites

- Python 3.8+

## Getting Started

### Environment Setup

1. Clone the repository

```bash
git clone https://gitlab.com/nhlstendenIT/it2024/semester-21/it2a-weather-claim-history-map/weather-project.git
cd weather-project
```

2. Copy the environment file and configure your variables

```bash
cp .env.example .env
```

3. Set up the backend:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r backend/requirements.txt
```

## Running the Application

### Backend

1. Activate the virtual environment (if not already activated):

```bash
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Start the backend server:

```bash
cd backend
python -m src.main
```

The backend will be available at `http://localhost:5001`

### Frontend

1. In a new terminal, start the frontend development server:

```bash
cd frontend
python -m http.server 5050
```

The frontend will be available at `http://localhost:5050`

## Browser Extension Setup

### Chrome Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" by toggling the switch in the top-right corner
3. Click "Load unpacked" button
4. Browse to the `unigarant_alert_extension` directory in your project folder and select it
5. The extension should now appear in your extensions list and be active
6. You can pin it to your toolbar by clicking the extensions icon in the toolbar and then the pin icon next to the extension

### Firefox Installation

1. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on..."
3. Browse to the `unigarant_alert_extension` directory and select the `manifest.json` file
4. The extension should now be temporarily installed and active

## API Documentation

The API documentation is available through Swagger UI when the backend is running:

- Swagger UI: `http://localhost:8000/swagger`

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/
```

## Browser Extension

### Installation

1. Navigate to the extension directory:

```bash
cd unigarant_alert_extension
```

2. Follow browser-specific installation instructions for development mode:

- Chrome: Open `chrome://extensions/`, enable "Developer mode", and click "Load unpacked"
