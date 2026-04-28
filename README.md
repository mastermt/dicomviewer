# DICOM Medical Image Viewer

This project is a desktop application for viewing medical images in DICOM format.
It is built with `PyQt5` for the graphical interface and uses `pydicom` to read and process DICOM files.

## What this application does

- Opens DICOM (`.dcm`) files
- Displays patient/study metadata
- Renders grayscale and RGB medical images
- Supports interactive image navigation:
  - Zoom in/out (mouse wheel, buttons, and keyboard shortcuts)
  - Pan (drag mode)
  - Reset view

## Main technologies

- Python
- `pydicom` (DICOM reading and metadata/image handling)
- `PyQt5` (desktop GUI)
- `numpy`
- `pylibjpeg` plugins (for extended compressed pixel data support)

## Installation with Anaconda (environment.yml)

1. Create the environment from the `environment.yml` file:

```bash
conda env create -f environment.yml
```

2. Activate the environment:

```bash
conda activate dicomviewer
```

3. Run the application:

```bash
python dicomviewer.py
```

## Installation with pip

1. (Optional but recommended) Create and activate a virtual environment.

On Windows (PowerShell):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python dicomviewer.py
```

## Keyboard shortcuts

- `Ctrl++`: zoom in
- `Ctrl+-`: zoom out
- `R`: reset view

## Data modules and database

The project now includes initial CRUD modules for:

- Patients registry
- Doctors registry

It uses SQLAlchemy and reads the connection string from `DATABASE_URL`.

- Default (local test): SQLite
  - `sqlite:///dicomviewer.db`
- Production example: PostgreSQL
  - `postgresql+psycopg2://user:password@host:5432/dbname`

On Windows PowerShell, example before running the app:

```bash
$env:DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/dicomviewer"
python dicomviewer.py
```

## Troubleshooting

- **PowerShell blocks virtual environment activation**
  - Error example: script execution is disabled.
  - Run PowerShell as current user and allow local scripts:
    - `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - Then activate again: `.\.venv\Scripts\Activate.ps1`

- **Qt platform plugin error on startup**
  - If the app fails to open with a Qt/plugin-related message, reinstall GUI packages:
    - `pip install --upgrade --force-reinstall PyQt5`
  - If using Conda, recreate the environment from `environment.yml`.

- **Compressed DICOM image cannot be decoded**
  - Make sure JPEG plugins are installed:
    - `pylibjpeg`
    - `pylibjpeg-libjpeg`
    - `pylibjpeg-openjpeg`
  - Reinstall with:
    - `pip install --upgrade pylibjpeg pylibjpeg-libjpeg pylibjpeg-openjpeg`

- **Environment creation fails with Python version constraints**
  - Verify that your Conda installation supports the Python version in `environment.yml`.
  - If needed, change the Python version in `environment.yml` to one available in your setup and recreate the environment.

## Known limitations

- Multi-frame DICOM files currently display only the first frame.
- The viewer does not include cine playback for time series.
- Advanced clinical tools are not implemented yet (window/level controls, measurements, annotations, MPR, etc.).
- No PACS/DICOM network integration (C-FIND, C-MOVE, C-STORE) is included.
- This project is intended for visualization and learning workflows, not for diagnostic use.
