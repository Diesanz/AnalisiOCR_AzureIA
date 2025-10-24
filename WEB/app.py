from flask import render_template
from . import create_app
app = create_app()

@app.route('/')
def index():
    """
    Muestra la página principal (index.html) 
    con el selector de fichero.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)