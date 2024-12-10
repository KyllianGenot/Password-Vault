from flask import Flask, render_template, request, redirect, flash, session, get_flashed_messages
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Base URL for the API endpoints
API_URL = "http://server1:5000"

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_code=404, error_message="Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_code=500, error_message="Internal Server Error"), 500

@app.route("/")
def home():
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Call the API to register the user
        response = requests.post(f"{API_URL}/signup", json={
            "username": username,
            "email": email,
            "password": password
        })

        if response.status_code == 200:
            flash("Signup successful! Please log in.", "success")
            return redirect("/login")
        else:
            error_message = response.json().get("error", "An unknown error occurred.")
            flash(f"Signup failed: {error_message}", "danger")
            return redirect("/signup")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")  # Username or email
        password = request.form.get("password")

        # Call the API to log in the user
        response = requests.post(f"{API_URL}/login", json={
            "identifier": identifier,
            "password": password
        })

        if response.status_code == 200:
            # Login successful
            user_info = response.json()
            session["logged_in"] = True
            session["username"] = user_info["username"]
            session["email"] = user_info["email"]
            flash("Login successful!", "success")
            return redirect("/profile")
        else:
            # Display specific error message
            error_message = response.json().get("error", "An unknown error occurred.")
            flash(error_message, "danger")
            return redirect("/login")

    return render_template("login.html")

@app.route("/profile")
def profile():
    if "logged_in" not in session:
        flash("You need to log in to view this page.", "danger")
        return redirect("/login")

    return render_template("profile.html", username=session.get("username"), email=session.get("email"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
