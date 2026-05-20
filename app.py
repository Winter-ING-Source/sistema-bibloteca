from flask import Flask, render_template, request
import psycopg2
import subprocess
import os  # <--- IMPORTANTE: Necesario para leer variables del entorno

app = Flask(__name__)

# --- CONFIGURACIÓN DB ADAPTADA A LA NUBE ---
# Render nos da una URL completa. Si existe, la usamos; si no, usa tus credenciales directas de la nube.
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://biblioteca_db_nube_user:PToNuNjZpN3kPuU1ZERjSU3dgyolIGxV@dpg-d87229m7r5hc738d4ta0-a.ohio-postgres.render.com/biblioteca_db_nube')

def obtener_conexion():
    # Esta función permite conectarse usando la URL directa de Render de forma limpia
    return psycopg2.connect(DATABASE_URL)

def extraer_catalogo_completo():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT l.id_libro, l.titulo, a.nombre, g.nombre, l.disponible 
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN generos g ON l.id_genero = g.id_genero
        ORDER BY l.titulo;
    """)
    catalogo = cursor.fetchall()
    cursor.close()
    conexion.close()
    return catalogo

def extraer_datos_usuario(usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT l.titulo, a.nombre, g.nombre, l.disponible 
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN generos g ON l.id_genero = g.id_genero;
    """)
    libros_crudos = cursor.fetchall()
    
    query = """
        SELECT DISTINCT g.nombre, a.nombre 
        FROM historial_lectura h
        JOIN usuarios u ON h.id_usuario = u.id_usuario
        JOIN libros l ON h.id_libro = l.id_libro
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN generos g ON l.id_genero = g.id_genero
        WHERE u.nombre = %s AND h.calificacion >= 4;
    """
    cursor.execute(query, (usuario,))
    gustos = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return libros_crudos, gustos

def generar_lisp(libros, usuario, gustos):
    with open("datos_intermedios.lisp", "w", encoding="utf-8") as f:
        f.write("(\n")
        for titulo, autor, genero, disponible in libros:
            f.write(f'  (libro "{titulo}" "{autor}" "{genero}")\n')
            f.write(f'  (disponible "{titulo}" "{disponible}")\n')
        if gustos:
            for genero, autor in gustos:
                f.write(f'  (le_gusto "{usuario}" "{genero}" "{autor}")\n')
        f.write(")\n")

def ejecutar_pipeline(usuario):
    try:
        libros, gustos = extraer_datos_usuario(usuario)
        if not gustos:
            return None, "El usuario no existe o no tiene historial."
            
        generar_lisp(libros, usuario, gustos)
        
        # MODIFICACIÓN CRÍTICA: En Linux el compilador se llama "sbcl", sin el ".exe"
        proceso_lisp = subprocess.run(["sbcl", "--script", "traductor.lisp"], capture_output=True, text=True)
        if proceso_lisp.returncode != 0:
            return None, f"Error en LISP: {proceso_lisp.stderr}"
        
        comando_prolog = [
            "swipl", "-q", "-s", "reglas.pl", 
            "-g", f"recomendar('{usuario}', Libro), writeln(Libro), fail; halt", 
            "-t", "halt"
        ]
        resultado = subprocess.run(comando_prolog, capture_output=True, text=True)
        
        salida = resultado.stdout.strip().split('\n')
        lista_unica = list(dict.fromkeys([r.strip() for r in salida if r.strip()]))
        return lista_unica, None
        
    except Exception as e:
        return None, f"Error interno: {str(e)}"

def registrar_en_db(nombre, ids_libros):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO usuarios (nombre) VALUES (%s) RETURNING id_usuario;", (nombre,))
    id_usuario = cursor.fetchone()[0]
    
    for id_libro in ids_libros:
        cursor.execute("""
            INSERT INTO historial_lectura (id_usuario, id_libro, calificacion) 
            VALUES (%s, %s, 5);
        """, (id_usuario, id_libro))
        
    conexion.commit()
    cursor.close()
    conexion.close()

# --- RUTAS WEB ---
@app.route('/', methods=['GET', 'POST'])
def index():
    recomendaciones = []
    error = None
    mensaje_exito = request.args.get('exito')
    usuario_consultado = ""
    catalogo = extraer_catalogo_completo()
    
    if request.method == 'POST':
        usuario_consultado = request.form.get('usuario')
        recomendaciones, error = ejecutar_pipeline(usuario_consultado)
        
    return render_template('index.html', recomendaciones=recomendaciones, 
                           usuario_consultado=usuario_consultado, 
                           error=error, exito=mensaje_exito, catalogo=catalogo)

@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    nuevo_nombre = request.form.get('nuevo_nombre')
    ids_libros = request.form.getlist('libros_leidos') 
    try:
        registrar_en_db(nuevo_nombre, ids_libros)
        catalogo = extraer_catalogo_completo()
        return render_template('index.html', catalogo=catalogo, 
                               usuario_consultado=nuevo_nombre, 
                               exito=f"¡{nuevo_nombre} registrado con éxito! Ya puedes consultarlo abajo.")
    except Exception as e:
        return render_template('index.html', catalogo=extraer_catalogo_completo(), 
                               error=f"Error al registrar: {str(e)}")

# MODIFICACIÓN CRÍTICA: En la nube el puerto lo asigna el servidor dinámicamente
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)