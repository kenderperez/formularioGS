from app import app, mysql
from werkzeug.security import generate_password_hash

with app.app_context():
    cur = mysql.connection.cursor()

    print("1. Apagando seguridad de llaves foráneas temporalmente...")
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

    print("2. Borrando la tabla 'usuarios' defectuosa a la fuerza...")
    cur.execute("DROP TABLE IF EXISTS usuarios")

    print("3. Creando la tabla 'usuarios' con todas sus columnas...")
    cur.execute("""
        CREATE TABLE usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            rango VARCHAR(20) NOT NULL
        )
    """)

    print("4. Encendiendo seguridad de llaves foráneas de nuevo...")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

    print("5. Guardando el administrador con el nuevo sistema de seguridad...")
    usuario = 'admin'
    password_plana = '123456'
    hash_seguro = generate_password_hash(password_plana)
    rango = 'admin'

    cur.execute("INSERT INTO usuarios (username, password, rango) VALUES (%s, %s, %s)", 
                (usuario, hash_seguro, rango))
    
    mysql.connection.commit()
    print("--------------------------------------------------")
    print("¡ÉXITO TOTAL! Tabla reparada y administrador creado.")
    print(f"Usuario: {usuario}")
    print(f"Clave:   {password_plana}")
    print("--------------------------------------------------")