## Local hosting
Probably put this in a script

### Flask backend
`python backend/app.py`

### PostgreSQL
Access console: `psql -d impulse_db`
Check status: `pg_ctl status -D backend/postgres/db`

### Chrome extension
`python build_chrome_extension.py`
Load unpacked in `chrome://extensions`