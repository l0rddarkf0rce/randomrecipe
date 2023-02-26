"""
Main entry point for the web server
"""
from website import create_app

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)