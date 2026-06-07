# SpendWise

SpendWise is a full-stack personal finance tracker built with Flask, PostgreSQL, SQLAlchemy, HTML, and CSS.

This project started as a beginner CRUD app and has been improved step by step into an intermediate-level full-stack application with authentication, user-specific data, search, filters, dashboard summaries, and a styled frontend.

## Current Level

This is an intermediate full-stack project.

It includes:

- User signup
- User login and logout
- Session-based authentication
- Password hashing
- User-specific transactions
- PostgreSQL database storage
- SQLAlchemy models and relationships
- Create, read, update, and delete transactions
- Income and expense summaries
- Search by title or category
- Filter by all, income, or expense
- Flash messages for user feedback
- Protected dashboard route
- Responsive CSS styling

## Tech Stack

- Backend: Python, Flask
- Database: PostgreSQL
- ORM: Flask-SQLAlchemy
- Templates: Jinja2
- Frontend: HTML, CSS
- Authentication: Flask sessions
- Password security: Werkzeug password hashing
- Environment variables: python-dotenv

## Project Structure

```text
expense-tracker/
  app.py
  requirements.txt
  .env
  .env.example
  .gitignore
  README.md
  templates/
    index.html
    login.html
    signup.html
  static/
    style.css
```

## File Responsibilities

### `app.py`

Main Flask application file.

It handles:

- Flask app setup
- PostgreSQL connection
- SQLAlchemy models
- User signup
- User login and logout
- Session handling
- Dashboard route protection
- Transaction add, edit, delete
- Transaction search and filtering
- Summary calculations
- Flash messages

### `templates/login.html`

Login page.

It allows an existing user to enter:

- Email
- Password

If the credentials are correct, the user is logged in and sent to the dashboard.

### `templates/signup.html`

Signup page.

It allows a new user to create an account with:

- Name
- Email
- Password
- Confirm password

The password is saved as a hash, not plain text.

### `templates/index.html`

Dashboard page.

It shows:

- Total income
- Total expense
- Balance
- Add/update transaction form
- Search box
- Filter buttons
- Transactions table
- Edit and delete buttons
- Logged-in user name
- Logout link

### `static/style.css`

Frontend styling file.

It styles:

- Auth pages
- Dashboard card
- Forms
- Buttons
- Summary cards
- Search and filter controls
- Tables
- Flash messages
- Responsive mobile layout

### `requirements.txt`

List of Python packages required to run the project.

### `.env`

Local environment settings.

This file stores your real database connection string. It should not be pushed to GitHub.

### `.env.example`

Safe example file showing what environment variables are needed.

### `.gitignore`

Keeps local-only files out of version control, such as `.env`, virtual environments, Python cache files, and test coverage output.

## Database Models

### User

The `User` model stores account information.

Fields:

```text
id
name
email
password_hash
created_at
```

Important concepts:

- `email` is unique, so two users cannot use the same email.
- `password_hash` stores a protected password hash.
- A user can have many transactions.

### Transaction

The `Transaction` model stores income and expense records.

Fields:

```text
id
user_id
title
amount
type
category
created_at
```

Important concepts:

- `user_id` links each transaction to a user.
- `type` stores either `income` or `expense`.
- Each logged-in user only sees their own transactions.

## Routes

### `/`

Home route.

This route shows the login page. If the user is already logged in, they are redirected to the dashboard.

### `/login`

Login route.

Methods:

- `GET`: show login form
- `POST`: check email and password

### `/signup`

Signup route.

Methods:

- `GET`: show signup form
- `POST`: create new user account

### `/dashboard`

Protected dashboard route.

Methods:

- `GET`: show dashboard and transactions
- `POST`: add or update a transaction

Only logged-in users can access this route.

### `/delete/<transaction_id>`

Delete route.

Method:

- `POST`: delete selected transaction

The app checks that the transaction belongs to the logged-in user before deleting it.

### `/logout`

Logout route.

Clears the session and redirects the user to the login page.

## Main Features

### 1. Authentication

Users can create an account, login, and logout.

The app uses Flask sessions to remember which user is logged in.

Example:

```python
session["user_id"] = user.id
```

### 2. Password Hashing

Passwords are not saved directly.

The app uses:

```python
generate_password_hash(password)
check_password_hash(user.password_hash, password)
```

This makes authentication safer than storing plain text passwords.

### 3. Protected Dashboard

The dashboard is only available after login.

If a logged-out user opens `/dashboard`, they are redirected to login.

### 4. User-Specific Data

Each transaction is connected to a user through `user_id`.

This means:

- User A sees only User A's transactions.
- User B sees only User B's transactions.

### 5. CRUD Transactions

The app supports full CRUD:

- Create: add a transaction
- Read: show transactions in a table
- Update: edit an existing transaction
- Delete: remove a transaction

### 6. Summary Cards

The dashboard calculates:

```text
Total Income
Total Expense
Balance
```

Formula:

```text
Balance = Total Income - Total Expense
```

### 7. Filtering

Users can filter transactions by:

```text
All
Income
Expense
```

Examples:

```text
/dashboard
/dashboard?filter=income
/dashboard?filter=expense
```

### 8. Search

Users can search transactions by title or category.

Examples:

```text
/dashboard?search=food
/dashboard?filter=expense&search=rent
```

The backend uses case-insensitive search with `ilike`.

### 9. Flash Messages

The app shows one-time feedback messages such as:

```text
Transaction added successfully.
Transaction updated successfully.
Transaction deleted successfully.
Invalid email or password.
```

## Setup Instructions

### 1. Create and Activate Virtual Environment

From inside `expense-tracker/`:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Create PostgreSQL Database

Open PostgreSQL and create the database:

```sql
CREATE DATABASE expense_tracker_db;
```

### 4. Configure `.env`

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/expense_tracker_db
SECRET_KEY=change-this-to-a-long-random-secret
```

Replace `your_password` with your real PostgreSQL password.

Use a long random value for `SECRET_KEY` in real projects because Flask uses it to protect session and flash-message data.

### 5. Run the App

```bash
python3 app.py
```

Open:

```text
http://127.0.0.1:5000/
```

The login page is the home page.

## How To Use

1. Open `/signup`.
2. Create an account.
3. Login from `/` or `/login`.
4. Add income and expense transactions.
5. Use filters to view all, income, or expense transactions.
6. Use search to find transactions by title or category.
7. Edit or delete transactions from the table.
8. Logout when finished.

## What We Built Step By Step

1. Created a Flask app with `app.py`.
2. Added an HTML homepage with `templates/index.html`.
3. Added CSS styling with `static/style.css`.
4. Added `requirements.txt`.
5. Built a transaction form.
6. Read form data in Flask.
7. Added `.env` for database configuration.
8. Connected Flask to PostgreSQL using SQLAlchemy.
9. Created a `Transaction` model.
10. Saved form data into PostgreSQL.
11. Displayed saved transactions on the page.
12. Added total income, total expense, and balance.
13. Added delete transaction feature.
14. Added edit/update transaction feature.
15. Added flash messages.
16. Added transaction filters.
17. Added search by title/category.
18. Added `User` model and user relationship.
19. Added signup.
20. Added login/logout and session-based authentication.
21. Made login the home page and moved the app to `/dashboard`.

## Current App Level

This app is now an intermediate full-stack project because it includes:

- Authentication
- Session handling
- User-specific database records
- Relational models
- CRUD operations
- Search and filtering
- Dashboard calculations
- Server-side validation basics
- Professional project structure

## Future Improvements

To make this project more advanced, add:

- Pagination
- Better form validation
- Charts for income and expenses
- Monthly reports
- Password reset
- User profile page
- Flask Blueprints
- Database migrations with Flask-Migrate
- Automated tests
- Docker setup
- Deployment documentation

## Important Notes

- Existing old transactions without `user_id` may not show after login. This is expected because the app now shows only the logged-in user's transactions.
- `.env` contains sensitive database information and should not be committed publicly.
- `db.create_all()` is simple and useful for learning, but professional apps usually use migrations.
