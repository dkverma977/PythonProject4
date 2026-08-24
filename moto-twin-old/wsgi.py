"""
Production WSGI Entrypoint for Motor Management Hub
Usage:
  Linux/Container: gunicorn --bind 0.0.0.0:8000 wsgi:app
  Windows/Cross-platform: waitress-serve --port=8000 wsgi:app
"""

from flask_server import app

if __name__ == "__main__":
    app.run()
