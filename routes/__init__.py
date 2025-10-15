from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Do NOT import model modules here to avoid circular imports.
# Import models from application code (app factory) AFTER db.init_app(app).
