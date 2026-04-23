import datetime
import os
from flask import Flask, app, render_template,request
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    try:
        client = MongoClient(
            os.getenv("MONGODB_URI"),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True
        )
        client.admin.command('ping')
        app.db = client.microblog
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        print("Please check:")
        print("1. Your MongoDB URI in .env is correct")
        print("2. Your IP is whitelisted in MongoDB Atlas (Network Access)")
        print("3. Your credentials are correct")
        raise

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            entry_content = request.form.get("content", "").strip()
            if entry_content:
                formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
                app.db.entries.insert_one({"content": entry_content, "date": formatted_date})
            return redirect(url_for("home"))

        entries_with_date=[
            (
            entry["content"],
            entry["date"],
            datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d")
            ) for entry in app.db.entries.find({})
                    ]
        return render_template("home.html",entries=entries_with_date)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
