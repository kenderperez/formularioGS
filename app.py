from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import io
import functools
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '856212'
app.config['MYSQL_DB'] = 'visitas'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'clave_secreta'

mysql = MySQL(app)

# --- DECORADORES ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rango') != 'admin': return "Acceso denegado", 403
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS PWA (OFFLINE) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sw.js')
def sw():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json', mimetype='application/json')

@app.route('/api/enviar', methods=['POST'])
def recibir_formulario():
    try:
        data = request.json
        print(f"--> Recibiendo datos: {data}") # DEBUG: Ver en consola

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        cur = mysql.connection.cursor()
        
        # 1. Verificar si ya existe (Evitar duplicados)
        cur.execute("SELECT id FROM visitas WHERE id = %s", [data['id']])
        existe = cur.fetchone()

        if not existe:
            # 2. Insertar
            query = """INSERT INTO visitas (id, marca, modelo, placa, color, vehiculo_tipo, persona_responsable, cedula, email, telefono, genero, num_integrantes, num_masculino, num_femenino, num_menores, edad_promedio, procedencia, visitado_antes, ultima_visita, destino_particular, fecha_entrada, dias_permanencia, fecha_retorno, reserva_hotel, hotel_cual, tipo_alojamiento, fecha_creacion) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())"""
            
            cur.execute(query, (
                data['id'], 
                data['marca'],
                data['modelo'],
                data['placa'],
                data['color'],
                data['vehiculo_tipo'],
                data['persona_responsable'],
                data['cedula'],
                data['email'],
                data['telefono'],
                data['genero'],
                data['num_integrantes'],
                data['num_masculino'],
                data['num_femenino'],
                data['num_menores'],
                data['edad_promedio'],
                data['procedencia'],
                data['visitado_antes'],
                data['ultima_visita'],
                data['destino_particular'],
                data['fecha_entrada'],
                data['dias_permanencia'],
                data['fecha_retorno'],
                data['reserva_hotel'],
                data['hotel_cual'],
                data['tipo_alojamiento']
            ))
            mysql.connection.commit()
            print("--> Guardado en BD exitosamente")
        else:
            print("--> El ID ya existía, se omitió duplicado.")

        cur.close()
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"!!! ERROR EN API: {e}") # Esto te dirá exactamente qué falla en la consola
        return jsonify({"error": str(e)}), 500

# Esta ruta se mantiene para que el admin pueda ver el QR en la web
@app.route('/qr/<id>')
def generar_qr(id):
    img = qrcode.make(id)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# --- AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", [user])
        account = cur.fetchone()
        # Add this before line 128 in app.py
        print(f"DEBUG: Password from DB is: '{account['password']}'")
  
        if account and check_password_hash(account['password'], pw):
            session['user_id'] = account['id']
            session['username'] = account['username']
            session['rango'] = account['rango']
            return redirect(url_for('admin_panel'))
        return "Usuario o contraseña incorrectos"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- PANEL DE CONTROL --- (El resto queda exactamente igual a tu código)
@app.route('/admin')
@login_required
def admin_panel():
    placa = request.args.get('placa', '')
    fecha = request.args.get('fecha', '')
    
    cur = mysql.connection.cursor()
    
    # Construir query con filtros opcionales
    query = "SELECT * FROM visitas WHERE 1=1"
    params = []
    
    if placa:
        query += " AND placa LIKE %s"
        params.append(f"%{placa}%")
    
    if fecha:
        query += " AND fecha_creacion >= %s"
        params.append(fecha)
    
    query += " ORDER BY fecha_creacion DESC"
    
    cur.execute(query, params)
    visitas = cur.fetchall()
    return render_template('admin.html', visitas=visitas, username=session['username'], rango=session['rango'])

@app.route('/admin/exportar')
@login_required
@admin_required
def exportar_excel():
    placa = request.args.get('placa', '')
    cur = mysql.connection.cursor()
    cur.execute("SELECT fecha_creacion, marca, modelo, placa, color, vehiculo_tipo, persona_responsable, cedula, email, telefono, genero, num_integrantes, num_masculino, num_femenino, num_menores, edad_promedio, procedencia, visitado_antes, ultima_visita, destino_particular, fecha_entrada, dias_permanencia, fecha_retorno, reserva_hotel, hotel_cual, tipo_alojamiento FROM visitas WHERE placa LIKE %s", [f"%{placa}%"])
    datos = cur.fetchall()
    if not datos: return "No hay datos para exportar", 404

    df = pd.DataFrame(datos)
    df.columns = ['Fecha Creación', 'Marca', 'Modelo', 'Placa', 'Color', 'Tipo Vehículo', 'Persona Responsable', 'Cédula', 'Email', 'Teléfono', 'Género', 'Num Integrantes', 'Num Masculino', 'Num Femenino', 'Num Menores', 'Edad Promedio', 'Procedencia', 'Visitado Antes', 'Última Visita', 'Destino Particular', 'Fecha Entrada', 'Días Permanencia', 'Fecha Retorno', 'Reserva Hotel', 'Hotel', 'Tipo Alojamiento']
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Visitas')
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name=f"Reporte.xlsx")

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
@admin_required
def gestionar_usuarios():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nuevo_user = request.form['username']
        nuevo_pw = generate_password_hash(request.form['password'])
        rango = request.form['rango']
        cur.execute("INSERT INTO usuarios (username, password, rango) VALUES (%s, %s, %s)", (nuevo_user, nuevo_pw, rango))
        mysql.connection.commit()
    cur.execute("SELECT id, username, rango FROM usuarios")
    return render_template('usuarios.html', usuarios=cur.fetchall())

@app.route('/lector')
@login_required
def lector_qr():
    return render_template('lector.html')

@app.route('/lectormatricula')
@login_required
def lector_matricula():
    return render_template('lectormatricula.html')

@app.route('/detalles_visita/<id>')
@login_required
def detalles_visita(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM visitas WHERE id = %s", [id])
    visita = cur.fetchone()
    if visita: return render_template('detalles.html', v=visita)
    return "Error: Código QR no registrado o inválido", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')