import os
import psycopg2
from flask import Flask, request, redirect

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        database=os.environ.get('DB_NAME', 'tipan_db'),
        user=os.environ.get('DB_USER', 'tipan_user'),
        password=os.environ.get('DB_PASSWORD', '123456')
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id SERIAL PRIMARY KEY,
            texto VARCHAR(200) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        init_db()
        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == 'POST':
            texto = request.form.get('texto', '').strip()
            if texto:
                cur.execute('INSERT INTO mensajes (texto) VALUES (%s);', (texto,))
                conn.commit()
            cur.close()
            conn.close()
            return redirect('/')

        cur.execute('SELECT version();')
        db_version = cur.fetchone()[0]

        cur.execute('SELECT id, texto FROM mensajes ORDER BY id DESC;')
        registros = cur.fetchall()
        cur.close()
        conn.close()

        lista_html = "".join([f"<li><strong>#{r[0]}:</strong> {r[1]}</li>" for r in registros])
        if not lista_html:
            lista_html = "<li>Aún no hay registros guardados.</li>"

        return f"""
        <h1>Hola, soy Kevin Tipan</h1>
        <hr>
        <p><strong>Estado de la Base de Datos:</strong> Conectado ({db_version})</p>
        <hr>
        <h3>Guardar en PostgreSQL</h3>
        <form method="POST">
            <input type="text" name="texto" placeholder="Escribe un dato..." required>
            <button type="submit">Guardar</button>
        </form>
        <h3>Registros guardados (Volumen v_tipan):</h3>
        <ul>{lista_html}</ul>
        """
    except Exception as e:
        return f"<h1>Error de conexión:</h1><p>{e}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
