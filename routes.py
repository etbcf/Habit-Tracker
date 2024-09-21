import datetime
import uuid
from flask import Blueprint, g, render_template, request, redirect, url_for

pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")


@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}


def get_db():
    if "db" not in g:  # If no `db` in `g`, create it
        g.db = g.db_client.get_database("habit_tracker_db")  # Retrieve the db
    return g.db  # Return the database connection


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)


@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    db = get_db()  # Retrieve the database
    habits_on_date = db.habits.find({"added": {"$lte": selected_date}})
    completions = [
        habit["habit"] for habit in db.completions.find({"date": selected_date})
    ]

    return render_template(
        "index.html",
        habits=habits_on_date,
        selected_date=selected_date,
        completions=completions,
        title="Habit Tracker - Home",
    )


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()

    if request.form:
        db = get_db()  # Access the database
        db.habits.insert_one({
            "_id": uuid.uuid4().hex,
            "added": today,
            "name": request.form.get("habit")
        })

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today,
    )


@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    habit = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)

    db = get_db()  # Access the database
    db.completions.insert_one({"date": date, "habit": habit})

    return redirect(url_for("habits.index", date=date_string))
