# Import the os module so we can read environment variables.
import os

# Import datetime so we can store the date and time when a transaction is created.
from datetime import datetime

# Import wraps so custom decorators keep the original function names.
from functools import wraps

# Import load_dotenv so Python can read values from the .env file.
from dotenv import load_dotenv

# Import Flask to create the web application.
# Import flash to show one-time success or error messages to the user.
# Import redirect to send the user from one route/page to another.
# Import render_template to show HTML files from the templates folder.
# Import request to read data coming from forms and URLs.
# Import session to remember which user is logged in.
# Import url_for to generate URLs using function names.
from flask import Flask, flash, redirect, render_template, request, session, url_for

# Import SQLAlchemy so Python can work with the PostgreSQL database.
from flask_sqlalchemy import SQLAlchemy

# Import or_ so we can search in title OR category.
# Import text so we can run a small safe database update command.
from sqlalchemy import or_, text

# Import password hash helpers for the upcoming signup and login feature.
from werkzeug.security import check_password_hash, generate_password_hash

# Load the .env file so DATABASE_URL becomes available to this app.
load_dotenv()

# Create the main Flask application object.
app = Flask(__name__)

# Set a secret key from the environment.
# Flask needs this for flash messages and session-based features.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# Set the database connection URL from the DATABASE_URL value inside .env.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# Turn off extra SQLAlchemy modification tracking because we do not need it here.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the database object that we will use for models, queries, add, update, and delete.
db = SQLAlchemy(app)


# Create a User model.
# A user will be able to create an account and own many transactions.
class User(db.Model):
    # Use a clear table name instead of "user", because user can be confusing in SQL.
    __tablename__ = "users"

    # Create an id column.
    # Each user will have a unique id.
    id = db.Column(db.Integer, primary_key=True)

    # Store the user's name.
    name = db.Column(db.String(100), nullable=False)

    # Store the user's email.
    # unique=True means two users cannot use the same email.
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Store the safe hashed password, not the real plain password.
    password_hash = db.Column(db.String(255), nullable=False)

    # Store the date and time when the user account was created.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Connect one user to many transactions.
    # Later, user.transactions can show all transactions that belong to a user.
    transactions = db.relationship("Transaction", backref="user", lazy=True)


# Create a Transaction model.
# A model is the Python version of a database table.
class Transaction(db.Model):
    # Create an id column.
    # primary_key=True means every transaction will have a unique id.
    id = db.Column(db.Integer, primary_key=True)

    # Store the id of the user who owns this transaction.
    # nullable=True keeps old transactions working until login is fully added.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Create a title column.
    # db.String(100) means this text can be up to 100 characters.
    # nullable=False means this field cannot be empty.
    title = db.Column(db.String(100), nullable=False)

    # Create an amount column.
    # db.Float means this value can store decimal numbers like 5000.50.
    amount = db.Column(db.Float, nullable=False)

    # Create a type column.
    # This will store either income or expense.
    type = db.Column(db.String(20), nullable=False)

    # Create a category column.
    # Examples: Food, Rent, Salary, Transport.
    category = db.Column(db.String(50), nullable=False)

    # Create a created_at column.
    # default=datetime.utcnow means the current time is saved automatically.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Open the Flask application context.
# SQLAlchemy needs this context to know which Flask app/database it should use.
with app.app_context():
    # Create database tables from the models if they do not already exist.
    db.create_all()

    # Add user_id to the existing transaction table if it is missing.
    # db.create_all() creates new tables, but it does not reliably add new columns
    # to tables that already exist, so this keeps our current database safe.
    db.session.execute(
        text('ALTER TABLE "transaction" ADD COLUMN IF NOT EXISTS user_id INTEGER')
    )

    # Save the small table update.
    db.session.commit()


# Get the currently logged-in user from the session.
def get_current_user():
    # Read user_id from the session.
    user_id = session.get("user_id")

    # If there is no user_id, no user is logged in.
    if not user_id:
        return None

    # Find and return the logged-in user from the database.
    return db.session.get(User, user_id)


# Protect routes that require login.
def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        current_user = get_current_user()

        if not current_user:
            flash("Please login to access SpendWise.", "error")
            return redirect(url_for("login"))

        return view_function(current_user, *args, **kwargs)

    return wrapper


# Create the dashboard route.
# GET shows the SpendWise dashboard.
# POST handles the transaction form submit.
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard(current_user):
    # Read edit_id from the URL.
    # Example URL: /?edit_id=3
    edit_id = request.args.get("edit_id")

    # Start with no transaction selected for editing.
    transaction_to_edit = None

    # If edit_id exists in the URL, the user wants to edit a transaction.
    if edit_id:
        # Find that transaction only if it belongs to the logged-in user.
        transaction_to_edit = Transaction.query.filter_by(
            id=edit_id,
            user_id=current_user.id
        ).first()

    # Check if the form was submitted.
    if request.method == "POST":
        # Read the hidden transaction_id from the form.
        # If this has a value, we update an existing transaction.
        # If this is empty, we create a new transaction.
        transaction_id = request.form.get("transaction_id")

        # Read the title value from the form.
        title = request.form.get("title")

        # Read the amount value from the form.
        amount = request.form.get("amount")

        # Read the type value from the form.
        # strip() removes extra spaces.
        # lower() converts text to lowercase.
        transaction_type = request.form.get("type", "").strip().lower()

        # Read the category value from the form.
        category = request.form.get("category")

        # Make sure title and category are clean strings.
        title = title.strip() if title else ""
        category = category.strip() if category else ""

        if not title or not category:
            flash("Title and category are required.", "error")
            return redirect(url_for("dashboard"))

        try:
            amount_value = float(amount)
        except (TypeError, ValueError):
            flash("Amount must be a valid number.", "error")
            return redirect(url_for("dashboard"))

        if amount_value <= 0:
            flash("Amount must be greater than zero.", "error")
            return redirect(url_for("dashboard"))

        # Only allow income or expense as valid transaction types.
        if transaction_type not in ["income", "expense"]:
            # Show an error message because the selected type is not valid.
            flash("Please select a valid transaction type.", "error")

            # If the type is invalid, go back to the dashboard without saving.
            return redirect(url_for("dashboard"))

        # If transaction_id exists, update an existing transaction.
        if transaction_id:
            # Find the transaction only if it belongs to the logged-in user.
            # If it does not exist, Flask will show a 404 page.
            transaction = Transaction.query.filter_by(
                id=transaction_id,
                user_id=current_user.id
            ).first_or_404()

            # Update the transaction title.
            transaction.title = title

            # Convert amount from text to number and update the transaction amount.
            transaction.amount = amount_value

            # Update the transaction type.
            transaction.type = transaction_type

            # Update the transaction category.
            transaction.category = category

            # Show a success message after updating.
            flash("Transaction updated successfully.", "success")
        else:
            # If transaction_id is empty, create a new Transaction object.
            new_transaction = Transaction(
                # Set the new transaction title.
                title=title,

                # Convert amount from text to number and set it.
                amount=amount_value,

                # Set the transaction type.
                type=transaction_type,

                # Set the transaction category.
                category=category,

                # Link this transaction to the logged-in user.
                user_id=current_user.id
            )

            # Add the new transaction to the database session.
            # At this point, it is prepared for saving but not saved yet.
            db.session.add(new_transaction)

            # Show a success message after adding.
            flash("Transaction added successfully.", "success")

        # Save the add or update change permanently in the database.
        db.session.commit()

        # After saving, redirect back to the dashboard.
        # This refreshes the list and clears the form.
        return redirect(url_for("dashboard"))

    # Read the selected filter from the URL.
    # Example URLs: /, /?filter=income, /?filter=expense
    selected_filter = request.args.get("filter", "all")

    # Read search text from the URL.
    # Example URL: /?search=food
    search_text = request.args.get("search", "").strip()

    # Start a database query for transactions.
    query = Transaction.query.filter_by(user_id=current_user.id)

    # If the selected filter is income, only show income transactions.
    if selected_filter == "income":
        query = query.filter_by(type="income")

    # If the selected filter is expense, only show expense transactions.
    elif selected_filter == "expense":
        query = query.filter_by(type="expense")

    # If the selected filter is anything else, use all transactions.
    else:
        selected_filter = "all"

    # If the user typed something in search, filter title or category.
    if search_text:
        # The percent signs mean: match text before or after the search word too.
        search_pattern = f"%{search_text}%"

        # ilike means case-insensitive search.
        # This searches in title OR category.
        query = query.filter(
            or_(
                Transaction.title.ilike(search_pattern),
                Transaction.category.ilike(search_pattern)
            )
        )

    # Get filtered transactions from the database.
    # order_by(...desc()) means newest transactions show first.
    transactions = query.order_by(Transaction.created_at.desc()).all()

    # Get all transactions for summary totals.
    # This keeps total income, total expense, and balance based on all data.
    all_transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    # Start total income from zero.
    total_income = 0

    # Start total expense from zero.
    total_expense = 0

    # Go through each transaction one by one.
    for transaction in all_transactions:
        # If the transaction type is income, add its amount to total_income.
        if transaction.type == "income":
            total_income = total_income + transaction.amount

        # If the transaction type is expense, add its amount to total_expense.
        elif transaction.type == "expense":
            total_expense = total_expense + transaction.amount

    # Calculate the remaining balance.
    # Formula: income minus expense.
    balance = total_income - total_expense

    # Show the index.html page and send all required data to it.
    return render_template(
        # This is the HTML file inside the templates folder.
        "index.html",

        # Send all transactions so the table can display them.
        transactions=transactions,

        # Send total income for the summary card.
        total_income=total_income,

        # Send total expense for the summary card.
        total_expense=total_expense,

        # Send balance for the summary card.
        balance=balance,

        # Send selected transaction data if the user is editing.
        transaction_to_edit=transaction_to_edit,

        # Send the selected filter so HTML can highlight the active filter button.
        selected_filter=selected_filter,

        # Send the search text so the search input keeps its value after submit.
        search_text=search_text,

        # Send the logged-in user to the template.
        current_user=current_user
    )


# Create a delete route.
# The transaction_id comes from the URL.
# Example URL: /delete/5
@app.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(current_user, transaction_id):
    # Find the transaction only if it belongs to the logged-in user.
    # If it does not exist, Flask will show a 404 page.
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    # Mark this transaction for deletion.
    db.session.delete(transaction)

    # Save the delete change permanently in the database.
    db.session.commit()

    # Show a success message after deleting.
    flash("Transaction deleted successfully.", "success")

    # After deleting, redirect back to the dashboard.
    return redirect(url_for("dashboard"))


# Create the signup route.
# GET shows the signup form.
# POST creates a new user account.
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # Check if the signup form was submitted.
    if request.method == "POST":
        # Read the name from the form.
        name = request.form.get("name", "").strip()

        # Read the email, remove spaces, and convert it to lowercase.
        email = request.form.get("email", "").strip().lower()

        # Read the password from the form.
        password = request.form.get("password", "")

        # Read the confirm password field from the form.
        confirm_password = request.form.get("confirm_password", "")

        # Make sure the name field is not empty.
        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("signup"))

        # Make sure the email field is not empty.
        if not email:
            flash("Email is required.", "error")
            return redirect(url_for("signup"))

        # Make sure the password has at least 6 characters.
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("signup"))

        # Make sure password and confirm password are the same.
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        # Check if another user already has this email.
        existing_user = User.query.filter_by(email=email).first()

        # If email already exists, do not create another account.
        if existing_user:
            flash("Email already exists. Please use another email.", "error")
            return redirect(url_for("signup"))

        # Convert the plain password into a safe password hash.
        password_hash = generate_password_hash(password)

        # Create a new User object.
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )

        # Add the new user to the database session.
        db.session.add(new_user)

        # Save the new user permanently in the database.
        db.session.commit()

        # Show success message after account creation.
        flash("Account created successfully. Please login now.", "success")

        # Redirect to the login page after signup.
        return redirect(url_for("login"))

    # Show the signup.html page.
    return render_template("signup.html")


# Create the login route.
# GET shows the login form.
# POST checks email and password.
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    # If the user is already logged in, send them to the dashboard.
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    # Check if the login form was submitted.
    if request.method == "POST":
        # Read email from the form and normalize it.
        email = request.form.get("email", "").strip().lower()

        # Read password from the form.
        password = request.form.get("password", "")

        # Find the user with this email.
        user = User.query.filter_by(email=email).first()

        # If user does not exist or password is wrong, show an error.
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        # Store the user's id in the session.
        # This means the browser is now logged in as this user.
        session["user_id"] = user.id

        # Show a success message.
        flash("Logged in successfully.", "success")

        # Send the user to the SpendWise dashboard.
        return redirect(url_for("dashboard"))

    # Show the login.html page.
    return render_template("login.html")


# Create the logout route.
@app.route("/logout")
def logout():
    # Remove user_id from the session.
    session.pop("user_id", None)

    # Show a success message.
    flash("Logged out successfully.", "success")

    # Send the user to the login page.
    return redirect(url_for("login"))


# This checks whether this file is being run directly.
if __name__ == "__main__":
    # Start the Flask development server.
    # debug=True shows helpful error messages while learning.
    app.run(debug=True)
