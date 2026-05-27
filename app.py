from flask import Flask, render_template
#zed isnt understanding we HAVE Flask 

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)