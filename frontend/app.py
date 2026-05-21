from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "dashboard/index.html", titulo="Sistema de Gestión Educativa"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
