import logging
from app import create_app

logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=4000)
