from blog import app, db
from app import User

# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User)

if __name__ == "__main__":
    app.run(debug=True)