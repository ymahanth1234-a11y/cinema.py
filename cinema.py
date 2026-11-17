from flask import Flask, request, redirect, render_template_string, url_for

app = Flask(__name__)
ROWS, COLS, MAX_MEMBERS = "ABCDEF", 10, 10
SHOWS = {"1": "Avengers - 10:00 AM", "2": "Inception - 2:00 PM", "3": "Interstellar - 7:00 PM"}
booked = {s: set() for s in SHOWS}   # booked seats per show
members = []                         # temporary memory (max 10 members)

PAGE = """
<html><head><title>Cinema Booking</title><style>
body{font-family:Arial;background:#111;color:#eee;text-align:center}
.screen{background:#ddd;color:#111;width:60%;margin:15px auto;padding:6px;border-radius:0 0 40px 40px}
.seat{display:inline-block;margin:3px}.seat input{display:none}
.seat span{display:block;width:34px;padding:6px 0;background:#2e7d32;border-radius:6px;cursor:pointer}
.seat input:checked+span{background:#f9a825}.taken span{background:#c62828;cursor:not-allowed}
table{margin:auto;border-collapse:collapse}td,th{border:1px solid #555;padding:5px 10px}
</style></head><body>
<h1>🎬 Cinema Seat Booking</h1><p style="color:#ff0">{{ msg }}</p>
<form method="get">Show: <select name="show" onchange="this.form.submit()">
{% for k,v in shows.items() %}<option value="{{k}}" {{'selected' if k==show}}>{{v}}</option>{% endfor %}
</select></form>
<div class="screen">SCREEN</div>
<form method="post" action="/book"><input type="hidden" name="show" value="{{show}}">
{% for r in rows %}<div>{% for c in range(1, cols+1) %}{% set s = r ~ c %}
<label class="seat {{'taken' if s in taken}}"><input type="checkbox" name="seat" value="{{s}}"
{{'disabled' if s in taken}}><span>{{s}}</span></label>{% endfor %}</div>{% endfor %}
<p>Name <input name="name" required> Phone <input name="phone" required>
<button>Book Seats</button></p></form>
<h3>Members in Memory ({{ members|length }}/{{ maxm }})</h3>
<table><tr><th>#</th><th>Name</th><th>Phone</th><th>Show</th><th>Seats</th><th></th></tr>
{% for m in members %}<tr><td>{{loop.index}}</td><td>{{m.name}}</td><td>{{m.phone}}</td>
<td>{{shows[m.show]}}</td><td>{{m.seats|join(', ')}}</td>
<td><a href="/cancel/{{loop.index0}}" style="color:#f88">Cancel</a></td></tr>{% endfor %}</table>
</body></html>"""

@app.route("/")
def home():
    show = request.args.get("show", "1")
    return render_template_string(PAGE, shows=SHOWS, show=show, rows=ROWS, cols=COLS,
        taken=booked[show], members=members, maxm=MAX_MEMBERS, msg=request.args.get("msg", ""))

@app.route("/book", methods=["POST"])
def book():
    show, seats = request.form["show"], request.form.getlist("seat")
    if len(members) >= MAX_MEMBERS:
        msg = "Memory full! Only 10 members allowed."
    elif not seats:
        msg = "Please select at least one seat."
    elif booked[show] & set(seats):
        msg = "Some seats are already booked."
    else:
        members.append({"name": request.form["name"], "phone": request.form["phone"],
                        "show": show, "seats": seats})
        booked[show].update(seats)
        msg = f"Booked {', '.join(seats)} successfully!"
    return redirect(url_for("home", show=show, msg=msg))

@app.route("/cancel/<int:i>")
def cancel(i):
    if 0 <= i < len(members):
        m = members.pop(i)
        booked[m["show"]].difference_update(m["seats"])
    return redirect(url_for("home", msg="Booking cancelled."))

if __name__ == "__main__":
    app.run(debug=True)   # [127.0.0.1](http://127.0.0.1:5000)
