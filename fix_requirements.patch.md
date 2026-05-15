Found runtime errors preventing uvicorn startup:

1) `ModuleNotFoundError: No module named 'uvicorn'` earlier was PATH-related. Running via `python -m uvicorn ...` works.

2) Current blocker: `ModuleNotFoundError: No module named 'pptx'` coming from `services/file_loader.py` (`from pptx import Presentation`).

`services/file_loader.py` also imports: `openpyxl`, `PIL` (Pillow), `pytesseract`.

Repo has two requirements files:
- `requirements.txt` includes fastapi, uvicorn, requests, PyPDF2, PyMuPDF, python-dotenv, google-generativeai (missing pptx/openpyxl/Pillow/pytesseract).
- `requirement.txt` is empty.

Next fix is to update `requirements.txt` to include:
- python-pptx
- openpyxl
- pillow
- pytesseract

Also ensure Tesseract OCR is installed on the system if you plan to OCR images.

Then re-run:
- `python -m pip install -r requirements.txt`
- `python -m uvicorn main:app --reload --log-level debug --port 3200`

