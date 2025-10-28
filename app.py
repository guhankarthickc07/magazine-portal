from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, Magazine
from forms import RegistrationForm, LoginForm, MagazineForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(name=form.name.data, department=form.department.data, dob=form.dob.data,
                    passed_out_year=form.passed_out_year.data, location=form.location.data,
                    email=form.email.data, password=hashed_password, role="Student",
                    profile_img="default.jpg")
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Waiting for admin approval.", "info")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.is_approved:
                flash("Admin approval pending.", "warning")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "Admin":
        users = User.query.filter_by(is_approved=False).all()
        magazines = Magazine.query.filter_by(is_approved=False).all()
        return render_template("admin_dashboard.html", users=users, magazines=magazines)
    else:
        magazines = Magazine.query.filter_by(is_approved=True).all()
        return render_template("student_dashboard.html", magazines=magazines, user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))



@app.route("/approve_user/<int:user_id>")
@login_required
def approve_user(user_id):
    if current_user.role != "Admin":
        return redirect(url_for("dashboard"))
    user = User.query.get(user_id)
    user.is_approved = True
    db.session.commit()
    flash("User approved!", "success")
    return redirect(url_for("dashboard"))

@app.route("/approve_magazine/<int:magazine_id>")
@login_required
def approve_magazine(magazine_id):
    if current_user.role != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for("dashboard"))

    magazine = Magazine.query.get_or_404(magazine_id)
    magazine.is_approved = True
    db.session.commit()

    flash("Magazine approved successfully!", "success")
    return redirect(url_for("dashboard"))

import os
from werkzeug.utils import secure_filename
from flask import current_app

app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/submit_magazine", methods=["GET", "POST"])
@login_required
def submit_magazine():
    form = MagazineForm()
    if form.validate_on_submit():
        pdf = request.files["pdf_file"]
        image = request.files.get("image_file")

        # Save PDF
        if pdf and allowed_file(pdf.filename):
            pdf_filename = secure_filename(pdf.filename)
            pdf.save(os.path.join(app.config["UPLOAD_FOLDER"], pdf_filename))
        else:
            flash("Invalid PDF file.", "danger")
            return redirect(url_for("submit_magazine"))

        # Save Image (if provided)
        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        magazine = Magazine(
            title=form.title.data,
            description=form.description.data,
            pdf_file=pdf_filename,
            image_file=image_filename,  # Store image filename in DB
            user_id=current_user.id
        )

        db.session.add(magazine)
        db.session.commit()
        flash("Magazine submitted for admin approval!", "info")
        return redirect(url_for("dashboard"))

    return render_template("submit_magazine.html", form=form)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from transformers import pipeline
chatbot = pipeline("text-generation", model="gpt2")

@app.route("/ch")
def chatindex():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    
    # Generate a response using GPT-2
    response = chatbot(user_input, max_length=100, do_sample=True, top_p=0.95, top_k=50)[0]["generated_text"]
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
