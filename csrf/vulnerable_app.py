from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secure-random-secret-key'
csrf = CSRFProtect(app)
app.config.update(
    SECRET_KEY="kan21-local-demo-secret",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Fake local-only data used for the assignment demonstration.
DEMO_USER = {
    "username": "victim",
    "password": "password123",
    "email": "victim@example.test",
    "bio": "This is the original profile information.",
}


@app.route("/")
def index():
    return render_template("index.html", logged_in=session.get("username") is not None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == DEMO_USER["username"] and password == DEMO_USER["password"]:
            session["username"] = username
            return redirect(url_for("profile"))

        flash("Invalid demo credentials.", "error")

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if session.get("username") != DEMO_USER["username"]:
        return redirect(url_for("login"))

    if request.method == "POST":
        # INTENTIONALLY VULNERABLE FOR ISEC3004 LAB DEMONSTRATION.
        # The application trusts the authenticated session cookie but does not
        # require an anti-CSRF token and does not independently verify that the
        # logged-in user intentionally initiated this state-changing request.
        # This is the insecure design that KAN-22 will demonstrate.
        DEMO_USER["email"] = request.form.get("email", DEMO_USER["email"])
        DEMO_USER["bio"] = request.form.get("bio", DEMO_USER["bio"])
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        username=DEMO_USER["username"],
        email=DEMO_USER["email"],
        bio=DEMO_USER["bio"],
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Localhost only. This deliberately vulnerable application must not be
    # exposed to a public network or used with real data.
    app.run(host="127.0.0.1", port=5000, debug=False)
