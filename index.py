from app import create_app
import sys, traceback

try:
    app = create_app()
except Exception as e:
    # Tampilkan error langsung saat diakses
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def error():
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        return f"<pre>{tb_str}</pre>", 500