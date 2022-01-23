from flask import Flask, render_template
import sys
application = Flask(__name__)

@application.route("/")
def main():
    return render_template("main.html")


if __name__ == "__main__":
    application.run(host='0.0.0.0')