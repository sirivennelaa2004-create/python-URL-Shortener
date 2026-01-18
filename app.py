from flask import Flask, render_template, request, redirect
from models import db, URL
import validators
import random
import string

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    message = ""

    if request.method == "POST":
        original_url = request.form.get("original_url")

        if validators.url(original_url):
            short_code = generate_short_code()

            new_url = URL(
                original_url=original_url,
                short_code=short_code
            )
            db.session.add(new_url)
            db.session.commit()

            short_url = request.host_url + short_code
            message = "Short URL created successfully!"
        else:
            message = "Invalid URL. Please enter a valid URL."

    return render_template("index.html", short_url=short_url, message=message)


@app.route("/history")
def history():
    urls = URL.query.all()
    return render_template("history.html", urls=urls)


@app.route("/<short_code>")
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()

    if url:
        return redirect(url.original_url)
    else:
        return "URL not found", 404


if __name__ == "__main__":
    app.run(debug=True)    