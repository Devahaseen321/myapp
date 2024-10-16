from flask import Flask, request, render_template, redirect, url_for
import datetime
from collections import defaultdict

app = Flask(__name__)
filename = 'transactions.txt'
expenses_file = 'expenses.txt'  # New file for daily expenses

def load_transactions():
    """Load transactions from the file."""
    transactions = defaultdict(list)  # Group by date
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) != 4:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue  # Skip lines that don't have exactly 4 values
                date, type_, amount, remark = parts
                transactions[date.split()[0]].append((date, type_, float(amount), remark))
    except FileNotFoundError:
        pass
    return transactions

def save_transaction(date, type_, amount, remark):
    """Save a new transaction to the file."""
    with open(filename, 'a') as file:
        file.write(f"{date},{type_},{amount},{remark}\n")

def calculate_balance():
    """Calculate the current balance."""
    transactions = load_transactions()
    balance = 0.0
    for date, records in transactions.items():
        for _, type_, amount, _ in records:
            if type_ == 'debit':
                balance -= amount
            elif type_ == 'credit':
                balance += amount
    return balance

def load_expenses():
    """Load daily expenses from the file."""
    expenses = {}
    try:
        with open(expenses_file, 'r') as file:
            for line in file:
                date, amount_spent = line.strip().split(',')
                expenses[date] = float(amount_spent)
    except FileNotFoundError:
        pass
    return expenses

def save_expense(date, amount_spent):
    """Save a new daily expense to the file."""
    with open(expenses_file, 'a') as file:
        file.write(f"{date},{amount_spent}\n")

@app.route('/')
def index():
    """Render the add transaction page."""
    return render_template('index.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Add a new transaction and redirect to transactions view."""
    type_ = request.form['type']
    amount = float(request.form['amount'])
    remark = request.form['remark']
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_transaction(date, type_, amount, remark)
    return redirect(url_for('view_transactions'))

@app.route('/transactions')
def view_transactions():
    """Render the transactions page grouped by date."""
    transactions = load_transactions()
    balance = calculate_balance()
    return render_template('transactions.html', transactions=transactions, balance=balance)

@app.route('/balance')
def view_balance():
    """Render the balance page."""
    balance = calculate_balance()
    return render_template('balance.html', balance=balance)

@app.route('/expenses', methods=['GET', 'POST'])
def daily_expenses():
    """Render the daily expenses page."""
    if request.method == 'POST':
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        amount_spent = float(request.form['amount_spent'])
        save_expense(date, amount_spent)
        return redirect(url_for('daily_expenses'))

    expenses = load_expenses()
    total_spent = sum(expenses.values())
    return render_template('expenses.html', expenses=expenses, total_spent=total_spent)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
