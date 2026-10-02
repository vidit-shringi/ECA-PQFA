# Deployment

## A. Run the complete local research tool

### Windows PowerShell

```powershell
cd ECA-PQFA
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
eca-pqfa health\neca-pqfa serve
```

Open:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Linux/macOS

```bash
cd ECA-PQFA
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
eca-pqfa serve
```

## B. Update the existing Google Apps Script deployment

The repository includes a complete replacement Apps Script project under `apps-script/`.

In the existing ECA-PQFA Sheet:

1. Extensions -> Apps Script.
2. Replace `Code.gs` with `apps-script/Code.gs`.
3. Add an HTML file named `Index` and paste `apps-script/Index.html`.
4. Save.
5. Run `uiSetup` once and authorize if prompted.
6. Deploy -> Manage deployments -> edit the Web App deployment.
7. Keep Execute as: Me.
8. Keep access at the setting appropriate to your project. The package assumes the browser uses the Apps Script-hosted UI when login-required access is enabled.
9. Open the `/exec` URL.

## C. Project integration values

The public repository contains placeholders. Configure your own values: 

```text
ECA_PQFA_SPREADSHEET_ID=...
ECA_PQFA_APPS_SCRIPT_URL=...
```

## D. Research safety/integrity

Do not put real credentials, secrets, or private keys into the synthetic dataset.

Do not interpret HNDL outputs or algorithm-string detection as proof of security, insecurity, or a cryptanalytic break.
