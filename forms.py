from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import RadioField, SelectField, IntegerField, SelectMultipleField, HiddenField, widgets
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

# Nuevos formularios para el sistema de pedidos de pizza
class PedidoForm(FlaskForm):    
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=4, max=50, message='Ingrese un nombre válido')
    ])
    direccion = StringField('Dirección', validators=[
        DataRequired(message='La dirección es requerida'),
        Length(min=4, max=100, message='Ingrese una dirección válida')
    ])
    telefono = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es requerido'),
        Regexp(regex='^[0-9]{10}$', message='Ingrese un teléfono válido de 10 dígitos')
    ])
    fecha_compra = DateField('Fecha de compra', format='%Y-%m-%d', default=datetime.now)
        
    TAMAÑOS = [
        ('Chica', 'Chica $40'),
        ('Mediana', 'Mediana $80'),
        ('Grande', 'Grande $120')
    ]
    
    INGREDIENTES = [
        ('jamon', 'Jamón $10'),
        ('pina', 'Piña $10'),
        ('champinones', 'Champiñones $10')
    ]
    
    tamano = RadioField('Tamaño Pizza', choices=TAMAÑOS, default='Chica')
    ingredientes = SelectMultipleField('Ingredientes', choices=INGREDIENTES, option_widget=widgets.CheckboxInput())
    numero_pizzas = IntegerField('Núm. de Pizzas', validators=[
        DataRequired(message='Cantidad requerida'),
        NumberRange(min=1, max=10, message='Debe ser entre 1 y 10')
    ], default=1)
        
    pizza_index = HiddenField('Índice')
    submit = SubmitField('Agregar')

class BusquedaVentasForm(FlaskForm):
    TIPO_BUSQUEDA = [
        ('dia', 'Por día'),
        ('mes', 'Por mes')
    ]
    
    tipo_busqueda = RadioField('Tipo de búsqueda', choices=TIPO_BUSQUEDA, default='dia')
    fecha = DateField('Fecha', format='%Y-%m-%d', default=datetime.now)
    submit = SubmitField('Buscar')