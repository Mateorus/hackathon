from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # User id
    user_id = session["user_id"]

    # User's cash remains
    cash = db.execute("SELECT cash FROM users WHERE id = :id_u", id_u = user_id)

    # Differens between "buy" d-base and "sell" d-base: ammount of stocks (total)
    portfolio = db.execute("""SELECT b.symbol, (shares1 - ifnull(shares2,0)) as shares FROM
    (SELECT symbol, SUM(shares) AS shares1 FROM buy WHERE user_id = :id_u GROUP BY symbol) b
    LEFT JOIN
    (SELECT symbol, SUM(shares) AS shares2 FROM sell WHERE user_id = :id_u1 GROUP BY symbol) s
    ON (b.symbol = s.symbol)
    WHERE shares > 0""",
    id_u = user_id,
    id_u1 = user_id)

    # Initial variables
    subtotal = 0
    z = 0

    # Preparing the list of dicts with information from d-base
    for i in portfolio:

        # Current stock price
        quote = lookup(i["symbol"])

        # Add price to a "i"'s dictionaty
        portfolio[z]["price"] = quote["price"]

        # Add total: price * n's shares
        portfolio[z]["total"] = i["shares"] * quote["price"]

        # Subtotal and counter
        subtotal += portfolio[z]["total"]
        z += 1

    # User's cash and total value of all stocks
    total = subtotal + cash[0]["cash"]

    # Cash alone
    cash = cash[0]["cash"]

    # Render the final template
    return render_template("index.html", cash = cash, total = total, portfolio = portfolio)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get user input
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # Get quote
        quote = lookup(symbol)

        #Check if input correct
        if not symbol or not quote:
            return apology("No such symbol or quote")

        elif not shares or shares < 0:
            return apology("Incorrect amount of shares")

        # Get user_id and account informanition
        user_id = session["user_id"]
        acc = db.execute("SELECT * FROM users WHERE id = :id_u", id_u = user_id)

        # Check users funds
        if (quote["price"] * shares > acc[0]["cash"]):
            return apology("Not enought funds")

        # Apply transaction
        else:
            result = db.execute("INSERT INTO buy (user_id,symbol,shares,price) VALUES (:user_id,:symbol,:shares,:price)",
            user_id = user_id,
            symbol = symbol,
            shares = shares,
            price = quote["price"])

            # Check if transaction succed
            if not result:
                return apology("OOPS1!")

            # Price of the transaction
            total = acc[0]["cash"] - quote["price"] * shares

            # Change user's account
            result_c = db.execute("UPDATE users SET cash = :cash WHERE id = :user_id",
            cash = total,
            user_id = user_id)

            # Check if account's change succed
            if not result_c:
                return apology("OOPS!")

            # Return user to index page
            return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user_id = session["user_id"]

    history = db.execute("""SELECT 'Buy' tran, symbol, shares, price, time FROM buy WHERE user_id = :user_id
    UNION ALL SELECT 'Sell' tran, symbol, shares, price, time FROM sell WHERE user_id = :user_id ORDER BY time""",
    user_id = user_id)

    return render_template("history.html", history = history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Form via GET method
    if request.method == "GET":
        return render_template("quote.html")

    # User check qoute via POST method
    elif request.method == "POST":

        # Symbol of stock
        symbol = request.form.get("symbol")

        #Get quote as dictionary
        quote = lookup(symbol)

        # Check if quote == None
        if not quote:
            return apology("something's gone wrong")

        # Make template with current quote
        return render_template("quoted.html", text="A share of {} ({}) costs {}".format(quote["name"], quote["symbol"], quote["price"]))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

         # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username not used
        if rows and request.form.get("username") == rows[0]["username"]:
            return apology("sry, this username already exists", 403)

        # Ensure password was submitted
        elif request.form.get("password") != request.form.get("password_r"):
            return apology("repeat password correctly", 403)

        # Input is correct; Add user to the data base
        else:
            result = db.execute("INSERT INTO users (username,hash) VALUES (:username, :hash_h)",
            username = request.form.get("username"), hash_h = generate_password_hash(request.form.get("password")))

            # Check if adding a user succed
            if not result:
                return apology("Can't register! Try later", 403)

            # Log in
            else:
                # Remember which user has logged in
                session["user_id"] = result

                # Redirect user to home page
                return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # GET method
    if request.method == "GET":

        # User id
        user_id = session["user_id"]

        # Get users portfolio
        portfolio = db.execute("""SELECT b.symbol, (shares1 - ifnull(shares2,0)) as shares FROM
        (SELECT symbol, SUM(shares) AS shares1 FROM buy WHERE user_id = :id_u GROUP BY symbol) b
        LEFT JOIN
        (SELECT symbol, SUM(shares) AS shares2 FROM sell WHERE user_id = :id_u1 GROUP BY symbol) s
        ON (b.symbol = s.symbol)
        WHERE shares > 0""",
        id_u = user_id,
        id_u1 = user_id)

        # List of stock available for selling
        symbols = [x["symbol"] for x in portfolio]

        # Render template
        return render_template("sell.html", symbols = symbols)


    # Post method
    if request.method == "POST":

        # Get users input
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        # Get stock quote
        quote = lookup(symbol)

        # User id
        user_id = session["user_id"]

        # Users account informatio
        acc = db.execute("SELECT * FROM users WHERE id = :id_u", id_u = user_id)

        # Get ammount of specified stocks
        portfolio = db.execute("""SELECT b.symbol, (shares1 - ifnull(shares2,0)) as shares FROM
        (SELECT symbol, SUM(shares) AS shares1 FROM buy WHERE user_id = :id_u GROUP BY symbol) b
        LEFT JOIN
        (SELECT symbol, SUM(shares) AS shares2 FROM sell WHERE user_id = :id_u1 GROUP BY symbol) s
        ON (b.symbol = s.symbol)
        WHERE b.symbol = :symbol""",
        id_u = user_id,
        id_u1 = user_id,
        symbol = symbol)

        # Check if user has enought shares
        if portfolio[0]["shares"] >= shares:

            # Write down the transaction to d-base
            result = db.execute("INSERT INTO sell (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)",
            user_id = user_id,
            symbol = symbol,
            shares = shares,
            price = quote["price"])

            # Check if transaction's succed
            if not result:
                return apology("OOPS1!")

            # Update user's cash
            result1 = db.execute("UPDATE users SET cash = :cash WHERE id = :user_id",
            cash = acc[0]["cash"] + quote["price"] * shares,
            user_id = user_id)


            # Check if update's succed
            if not result1:
                return apology("OOPS1!")


            # Redirect to main page
            return redirect("/")


        # If not enought shares
        else:
            return apology("Not enought shares")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
