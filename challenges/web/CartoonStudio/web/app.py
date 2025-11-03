import os, uuid, string, secrets
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from datetime import datetime
from config import MONGO_URI, SECRET_KEY, LOG_DIR

app = Flask(__name__)
app.secret_key = SECRET_KEY

os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "app.log")
with open(log_path, 'w') as f:
    f.write("This is a log file for the Cartoon Studio web app.\n")

client = MongoClient(MONGO_URI)
db = client.get_default_database()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
alphabet = string.ascii_letters + string.digits

class User(UserMixin):
    def __init__(self, data):
        self._id = str(data.get("_id"))
        self.username = data.get("username")
        self.password = data.get("password")
        self.isAdmin = data.get("isAdmin", False)
        self.watch_count = data.get("watch_count", 0)

    def get_id(self):
        return self._id

def get_user_by_id(id_str):
    doc = db.users.find_one({"_id": ObjectId(id_str)})
    if not doc:
        return None
    return User(doc)

@login_manager.user_loader
def load_user(user_id):
    try:
        return get_user_by_id(user_id)
    except Exception:
        return None

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        doc = db.users.find_one({"_id": ObjectId(current_user.get_id())})
        if not doc or not doc.get("isAdmin", False):
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
@login_required
def dashboard():
    try:
        cartoons = list(db.cartoons.find())
        for c in cartoons:
            c["_id"] = str(c["_id"])
        user_doc = db.users.find_one({"_id": ObjectId(current_user.get_id())})
        is_admin = user_doc.get("isAdmin", False)
        return render_template("dashboard.html", cartoons=cartoons, user=current_user, is_admin=is_admin)
    except Exception as e:
        return redirect(url_for("register"))
    
@app.route("/watch/<cartoon_id>")
@login_required
def watch(cartoon_id):
    try:
        c = db.cartoons.find_one({"_id": ObjectId(cartoon_id)})
        if not c:
            flash("Cartoon not found", "danger")
            return redirect(url_for("dashboard"))
        db.cartoons.update_one({"_id": ObjectId(cartoon_id)}, {"$inc": {"views": 1}})
        db.users.update_one({"_id": ObjectId(current_user.get_id())}, {"$inc": {"watch_count": 1}})
        return render_template("watch.html", cartoon=c)
    except Exception as e:
        return redirect(url_for("dashboard"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":      
        try:
            username = str(uuid.uuid4())
            password = ''.join(secrets.choice(alphabet) for i in range(8))
            user = {"username": username, "password": password, "isAdmin": False, "watch_count": 0, "created_at": datetime.utcnow()}
            db.users.insert_one(user)
            return render_template("register_success.html", username=username, password=password)
        except Exception as e:
            flash("Registration failed", "danger")
            return render_template("register.html")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = request.get_json()          
            username = data.get("username")      
            password = data.get("password")

            user_doc = db.users.find_one({"username": username, "password": password})
            if not user_doc:
                flash("Invalid Credentials", "warning")
                return render_template("login.html")
            login_user(User(user_doc))
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash("Login failed", "danger")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("login"))

@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("admin.html")

@app.route("/admin/top-users")
@login_required
@admin_required
def admin_top_users():
    top = list(db.users.find({}, {"password": 0}).sort("watch_count", DESCENDING).limit(10))
    for u in top:
        u["id"] = str(u["_id"])
    return {"top_users": top}

@app.route("/admin/download-logs/<path:filename>")
@login_required
@admin_required
def download_logs(filename):
    try:
        requested = os.path.join(LOG_DIR, filename)
        return send_file(requested, as_attachment=True)
    except Exception as e:
        abort(404)

@app.route("/admin/top")
@login_required
@admin_required
def admin_top_page():
    top = list(db.users.find({}, {"password": 0}).sort("watch_count", DESCENDING).limit(10))
    return render_template("admin.html", top_users=top)

@app.errorhandler(403)
def forbidden(e):
    return "403 Forbidden", 403

@app.errorhandler(404)
def not_found(e):
    return "404 Not Found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6021)