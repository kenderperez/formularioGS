from app import app, mysql

with app.app_context():
    cur = mysql.connection.cursor()

    print("1. Apagando seguridad de llaves foráneas temporalmente...")
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

    print("2. Agregando nuevas columnas a la tabla 'visitas'...")

    # Agregar columnas una por una para evitar errores
    alter_queries = [
        "ALTER TABLE visitas ADD COLUMN marca VARCHAR(100)",
        "ALTER TABLE visitas ADD COLUMN modelo VARCHAR(100)",
        "ALTER TABLE visitas ADD COLUMN placa VARCHAR(20)",
        "ALTER TABLE visitas ADD COLUMN color VARCHAR(50)",
        "ALTER TABLE visitas ADD COLUMN vehiculo_tipo VARCHAR(20)",
        "ALTER TABLE visitas ADD COLUMN persona_responsable VARCHAR(200)",
        "ALTER TABLE visitas ADD COLUMN cedula VARCHAR(20)",
        "ALTER TABLE visitas ADD COLUMN email VARCHAR(150)",
        "ALTER TABLE visitas ADD COLUMN telefono VARCHAR(20)",
        "ALTER TABLE visitas ADD COLUMN genero VARCHAR(20)",
        "ALTER TABLE visitas ADD COLUMN num_integrantes INT",
        "ALTER TABLE visitas ADD COLUMN num_masculino INT",
        "ALTER TABLE visitas ADD COLUMN num_femenino INT",
        "ALTER TABLE visitas ADD COLUMN num_menores INT",
        "ALTER TABLE visitas ADD COLUMN edad_promedio DECIMAL(5,2)",
        "ALTER TABLE visitas ADD COLUMN procedencia VARCHAR(100)",
        "ALTER TABLE visitas ADD COLUMN visitado_antes VARCHAR(10)",
        "ALTER TABLE visitas ADD COLUMN ultima_visita DATE",
        "ALTER TABLE visitas ADD COLUMN destino_particular TEXT",
        "ALTER TABLE visitas ADD COLUMN fecha_entrada DATE",
        "ALTER TABLE visitas ADD COLUMN dias_permanencia INT",
        "ALTER TABLE visitas ADD COLUMN fecha_retorno DATE",
        "ALTER TABLE visitas ADD COLUMN reserva_hotel VARCHAR(10)",
        "ALTER TABLE visitas ADD COLUMN hotel_cual VARCHAR(200)",
        "ALTER TABLE visitas ADD COLUMN tipo_alojamiento VARCHAR(20)"
    ]

    for query in alter_queries:
        try:
            cur.execute(query)
            print(f"✓ Ejecutado: {query}")
        except Exception as e:
            print(f"⚠ Error en {query}: {e}")

    print("3. Encendiendo seguridad de llaves foráneas de nuevo...")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

    mysql.connection.commit()
    print("--------------------------------------------------")
    print("¡ÉXITO! Tabla 'visitas' actualizada con nuevas columnas.")
    print("--------------------------------------------------")