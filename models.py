from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode, io, uuid

from models import db, User, TucTuc, Viaje

app = Flask(__name__)
app.secret_key = "Coopah_2024!"  

# PostgreSQL en Railway
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:vPQEGCiFPAYdfKURWKFcQTwVPXLXMFCE@shortline.proxy.rlwy.net:24019/railway"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ----------------- LOGIN MANAGER -----------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- RUTAS -----------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        tuctucs = TucTuc.query.all()
        return render_template("dashboard.html", tuctucs=tuctucs)
    else:
        return redirect(url_for("registrar_viaje"))

@app.route("/registrar_tuctuc", methods=["GET","POST"])
@login_required
def registrar_tuctuc():
    if current_user.role != "admin":
        return "Acceso denegado"
    if request.method == "POST":
        nombre = request.form["nombre"]
        token = str(uuid.uuid4())
        nuevo = TucTuc(nombre=nombre, qr_token=token)
        db.session.add(nuevo)
        db.session.commit()
        flash("Tuc Tuc registrado con éxito")
        return redirect(url_for("dashboard"))
    return render_template("registrar_tuctuc.html")

@app.route("/qr/<int:id>")
@login_required
def qr(id):
    tuctuc = TucTuc.query.get_or_404(id)
    img = qrcode.make(f"http://localhost:5000/viaje/{tuctuc.qr_token}")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/viaje/<string:token>", methods=["GET","POST"])
@login_required
def registrar_viaje(token):
    tuctuc = TucTuc.query.filter_by(qr_token=token).first_or_404()
    if request.method == "POST":
        pasajeros = int(request.form["pasajeros"])
        obs = request.form.get("observaciones", "")
        if pasajeros > 3:
            flash("Máximo 3 pasajeros (a menos que sean niños en piernas)")
        else:
            viaje = Viaje(tuctuc_id=tuctuc.id, pasajeros=pasajeros, observaciones=obs)
            db.session.add(viaje)
            db.session.commit()
            flash("Viaje registrado con éxito")
            return redirect(url_for("registrar_viaje", token=token))
    return render_template("registrar_viaje.html", tuctuc=tuctuc, qr=True)

@app.route("/viajes/<int:tuctuc_id>")
@login_required
def ver_viajes(tuctuc_id):
    if current_user.role != "admin":
        return "Acceso denegado"
    tuctuc = TucTuc.query.get_or_404(tuctuc_id)
    viajes = Viaje.query.filter_by(tuctuc_id=tuctuc.id).all()
    return render_template("ver_viajes.html", tuctuc=tuctuc, viajes=viajes)

@app.route("/registrar_viaje_admin/<int:tuctuc_id>", methods=["GET","POST"])
@login_required
def registrar_viaje_admin(tuctuc_id):
    if current_user.role != "admin":
        return "Acceso denegado"
    tuctuc = TucTuc.query.get_or_404(tuctuc_id)
    if request.method == "POST":
        pasajeros = int(request.form["pasajeros"])
        obs = request.form.get("observaciones", "")
        if pasajeros > 6:
            flash("Máximo 6 pasajeros")
        else:
            viaje = Viaje(tuctuc_id=tuctuc.id, pasajeros=pasajeros, observaciones=obs)
            db.session.add(viaje)
            db.session.commit()
            flash("Viaje registrado con éxito")
            return redirect(url_for("dashboard"))
    return render_template("registrar_viaje.html", tuctuc=tuctuc, qr=False)

@app.route("/eliminar_viaje/<int:viaje_id>", methods=["POST"])
@login_required
def eliminar_viaje(viaje_id):
    if current_user.role != "admin":
        return "Acceso denegado"
    viaje = Viaje.query.get_or_404(viaje_id)
    tuctuc_id = viaje.tuctuc_id
    db.session.delete(viaje)
    db.session.commit()
    flash("Viaje eliminado con éxito")
    return redirect(url_for("ver_viajes", tuctuc_id=tuctuc_id))

# ----------------- INICIALIZACIÓN DB Y ADMIN -----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # Crear o actualizar usuario admin
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            # Crear admin si no existe
            admin = User(
                username="admin", 
                password=generate_password_hash("1234"),  # contraseña: 1234
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado correctamente")
        else:
            # Actualizar contraseña en caso de que sea texto plano o incorrecta
            admin.password = generate_password_hash("1234")
            db.session.commit()
            print("Contraseña del admin actualizada correctamente")
            
    app.run(debug=True)
