from app import create_app

app = create_app()

if __name__ == "__main__":
    # Development server only. In production use: gunicorn -c deployment/gunicorn.conf.py run:app
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("FLASK_DEBUG", False))
