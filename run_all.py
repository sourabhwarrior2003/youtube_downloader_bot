import threading
from app import app as flask_app
from bot import create_bot_app

def run_flask():
    flask_app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    bot_app = create_bot_app()
    bot_app.run_polling()

    flask_thread.join()
