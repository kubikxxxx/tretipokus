# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template, request

# Third-party imports

# App imports
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User, Uzivatele

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired, Regexp


class FormFormular(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="You can't leave this empty"),
                                           Length(min=2, max=20,
                                                  message="Name must be between 2 and 20 characters long"),
                                           Regexp('^[A-Za-z]*$', message="Name must contain only letters")])

    surename = StringField('Surename', validators=[InputRequired(message="You can't leave this empty"),
                                                   Length(min=2, max=20,
                                                          message="Name must be between 2 and 20 characters long"),
                                                   Regexp('^[A-Za-z]*$', message="Name must contain only letters")])


# List to store users
user_list = []


@bp.route("/formular", methods=["GET", "POST"])
def formular():
    user_list.clear()
    users = Uzivatele.query.all()
    for user in users:
        user_list.append({"user_id": user.user_id, "name": user.name, "surename": user.surename})
    form = FormFormular()
    if form.validate_on_submit():
        new_user = Uzivatele(name=form.name.data, surename=form.surename.data)
        db.add(new_user)
        db.commit()
        user_list.append({"user_id": new_user.user_id, "name": new_user.name, "surename": new_user.surename})
        return render_template("formular.html", form=form, users=user_list)
    return render_template("formular.html", form=form, users=user_list)


@bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = Uzivatele.query.filter_by(user_id=user_id).first()
    form = FormFormular(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.surename = form.surename.data
        db.commit()

        # Aktualizace seznamu uživatelů
        user_list.clear()
        users = Uzivatele.query.all()
        for user in users:
            user_list.append({"user_id": user.user_id, "name": user.name, "surename": user.surename})

        return render_template("formular.html", form=form, users=user_list)
    return render_template("formular.html", form=form, user=user)


@bp.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    user = Uzivatele.query.filter_by(user_id=user_id).first()
    if user is None:
        # Aktualizace seznamu uživatelů
        user_list.clear()
        users = Uzivatele.query.all()
        for user in users:
            user_list.append({"user_id": user.user_id, "name": user.name, "surename": user.surename})
        return render_template("formular.html", form=FormFormular(), users=user_list)

    db.delete(user)
    db.commit()

    # Aktualizace seznamu uživatelů
    user_list.clear()
    users = Uzivatele.query.all()
    for user in users:
        user_list.append({"user_id": user.user_id, "name": user.name, "surename": user.surename})

    return render_template("formular.html", form=FormFormular(), users=user_list)


# Request management

@bp.before_app_request
def before_request():
    db()


# Request management
@bp.before_app_request
def before_request():
    db()


@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()


# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
bp.add_url_rule("/", view_func=static_views.index)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
    "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
    "/api/register",
    view_func=account_management_views.register_account,
    methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
    "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)