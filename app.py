from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import DevelopmentConfig
from models import db, User, Cliente, DetallePedido
from forms import LoginForm, RegisterForm, PedidoForm, BusquedaVentasForm
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Inicialización de la base de datos
db.init_app(app)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Archivo temporal para almacenar pizzas
TEMP_FILE = 'pizzas_temp.txt'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Funciones auxiliares para el sistema de pedidos
def get_precio_tamano(tamano):
    precios = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
    return precios.get(tamano, 0)

def get_precio_ingrediente():
    return 10  # Cada ingrediente cuesta $10

def guardar_pizzas_en_archivo(pizzas_temp):
    with open(TEMP_FILE, 'w') as f:
        for pizza in pizzas_temp:
            linea = f"{pizza['tamano']}|{pizza['ingredientes']}|{pizza['numero_pizzas']}|{pizza['subtotal']}\n"
            f.write(linea)

def leer_pizzas_desde_archivo():
    pizzas_temp = []
    if os.path.exists(TEMP_FILE):
        try:
            with open(TEMP_FILE, 'r') as f:
                lineas = f.readlines()
                for linea in lineas:
                    if linea.strip():
                        partes = linea.strip().split('|')
                        if len(partes) == 4:
                            pizza = {
                                'tamano': partes[0],
                                'ingredientes': partes[1],
                                'numero_pizzas': int(partes[2]),
                                'subtotal': float(partes[3])
                            }
                            pizzas_temp.append(pizza)
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
    return pizzas_temp

# Rutas de autenticación
@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(next_page or url_for('dashboard'))
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso', 'error')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

# Ruta principal del dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Nuevas rutas para el sistema de pedidos de pizza
@app.route('/pedidos', methods=['GET', 'POST'])
@login_required
def pedidos():
    # Si hay datos del formulario, usa esos, si no, crea un formulario nuevo
    form_data = request.form if request.method == 'POST' else None
    pedido_form = PedidoForm(form_data)
    
    # Obtener ventas del día
    today = datetime.now().date()
    ventas = Cliente.query.all()  
    ventas_filtradas = []

    for venta in ventas:
        fecha_db = venta.fecha_compra
        if isinstance(fecha_db, str):
            fecha_db = datetime.strptime(fecha_db, '%Y-%m-%d').date()
        
        if fecha_db == today:
            ventas_filtradas.append(venta)

    ventas_total = sum(venta.total for venta in ventas_filtradas)

    pizzas_temp = leer_pizzas_desde_archivo()

    if request.method == 'POST':                        
        if 'agregar' in request.form:
            # Validamos solo los campos de la pizza
            if pedido_form.tamano.validate(pedido_form) and pedido_form.ingredientes.validate(pedido_form) and pedido_form.numero_pizzas.validate(pedido_form):
                tamano = pedido_form.tamano.data
                ingredientes = pedido_form.ingredientes.data
                num_pizzas = pedido_form.numero_pizzas.data

                precio_tamano = get_precio_tamano(tamano)
                precio_ingredientes = len(ingredientes) * get_precio_ingrediente()
                subtotal = (precio_tamano + precio_ingredientes) * num_pizzas

                nueva_pizza = {
                    'tamano': tamano,
                    'ingredientes': ', '.join(ingredientes),
                    'numero_pizzas': num_pizzas,
                    'subtotal': subtotal
                }

                pizzas_temp.append(nueva_pizza)
                guardar_pizzas_en_archivo(pizzas_temp)

                flash('Pizza agregada al pedido', 'success')
                # En lugar de redirigir, renderizamos la plantilla manteniendo los datos del formulario
                return render_template('pedidos.html', 
                                     form=pedido_form, 
                                     pizzas=pizzas_temp,
                                     ventas=ventas_filtradas,
                                     ventas_total=ventas_total)
            else:
                flash('Por favor complete correctamente los datos de la pizza', 'error')
                
        elif 'quitar' in request.form:
            if pizzas_temp:
                index = int(request.form.get('pizza_index', 0))
                if 0 <= index < len(pizzas_temp):
                    pizzas_temp.pop(index)
                
                guardar_pizzas_en_archivo(pizzas_temp)

                flash('Pizza eliminada del pedido', 'success')
                # En lugar de redirigir, renderizamos la plantilla manteniendo los datos del formulario
                return render_template('pedidos.html', 
                                     form=pedido_form, 
                                     pizzas=pizzas_temp,
                                     ventas=ventas_filtradas,
                                     ventas_total=ventas_total)
                
        elif 'terminar' in request.form:
            if pizzas_temp and pedido_form.validate():
                total = sum(pizza['subtotal'] for pizza in pizzas_temp)
                
                fecha_compra = pedido_form.fecha_compra.data
                if isinstance(fecha_compra, str):
                    fecha_compra = datetime.strptime(fecha_compra, '%Y-%m-%d').date()

                nuevo_cliente = Cliente(
                    nombre=pedido_form.nombre.data,
                    direccion=pedido_form.direccion.data,
                    telefono=pedido_form.telefono.data,
                    fecha_compra=fecha_compra,
                    total=total
                )

                db.session.add(nuevo_cliente)
                db.session.commit()

                for pizza in pizzas_temp:
                    detalle = DetallePedido(
                        cliente_id=nuevo_cliente.id,
                        tamano=pizza['tamano'],
                        ingredientes=pizza['ingredientes'],
                        numero_pizzas=pizza['numero_pizzas'],
                        subtotal=pizza['subtotal']
                    )
                    db.session.add(detalle)

                db.session.commit()

                if os.path.exists(TEMP_FILE):
                    os.remove(TEMP_FILE)

                flash(f'¡Pedido completado! Total a pagar: ${total:.2f}', 'success')
                # Después de terminar el pedido, limpiamos el formulario creando uno nuevo
                return redirect(url_for('pedidos'))
            elif not pedido_form.validate():
                flash('Por favor, complete correctamente los datos del cliente', 'error')
            else:
                flash('No hay pizzas en el pedido', 'error')

    return render_template('pedidos.html', 
                         form=pedido_form, 
                         pizzas=pizzas_temp,
                         ventas=ventas_filtradas,
                         ventas_total=ventas_total)

@app.route('/ventas', methods=['GET', 'POST'])
@login_required
def ventas():
    busqueda_form = BusquedaVentasForm()
    resultados = []

    if request.method == 'POST' and busqueda_form.validate():
        tipo_busqueda = busqueda_form.tipo_busqueda.data
        fecha_busqueda = busqueda_form.fecha.data

        if tipo_busqueda == 'dia':
            ventas = Cliente.query.all()
            resultados = []

            for venta in ventas:
                fecha_db = venta.fecha_compra
                if isinstance(fecha_db, str):
                    fecha_db = datetime.strptime(fecha_db, '%Y-%m-%d').date()
                
                if fecha_db == fecha_busqueda:
                    resultados.append({
                        'nombre': venta.nombre,
                        'total': venta.total,
                        'fecha': venta.fecha_compra
                    })

        else:  # tipo_busqueda == 'mes'
            ventas = Cliente.query.filter(
                db.extract('year', Cliente.fecha_compra) == fecha_busqueda.year,
                db.extract('month', Cliente.fecha_compra) == fecha_busqueda.month
            ).all()

            resultados = [
                {
                    'nombre': venta.nombre,
                    'total': venta.total,
                    'fecha': venta.fecha_compra
                }
                for venta in ventas
            ]

    return render_template('ventas.html', form=busqueda_form, resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)