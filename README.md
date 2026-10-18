# Noor Collections — Business Management System

A Streamlit frontend for the `noor_collections` MySQL database: employee
login with roles, dashboard with revenue/inventory stats, product
management, order creation (via a stored procedure with stock locking),
and customer/employee management.

## 1. Install requirements

```bash
pip install -r requirements.txt
```

## 2. Set up the database

Run `backend.sql` in MySQL (Workbench, or the `mysql` CLI):

```bash
mysql -u root -p < backend.sql
```

## 3. Configure your database credentials

Copy the example secrets file and fill in your real MySQL details:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then edit `.streamlit/secrets.toml`:

```toml
[db]
host = "localhost"
port = 3306
user = "root"
password = "your_mysql_password"
database = "noor_collections"
```

`secrets.toml` is only for you — never share it or upload it publicly
(add it to `.gitignore` if you push this to GitHub).

## 4. Set demo employee passwords

The 3 sample employees in `backend.sql` start with placeholder password
hashes (real passwords should never sit in plain SQL). Run this once:

```bash
python setup_demo_passwords.py
```

Edit the `DB_CONFIG` and `DEMO_USERS` at the top of that file first if you
want different login credentials. Default demo logins after running it:

| Username         | Password        | Role               |
|------------------|-----------------|--------------------|
| fatima.noor      | admin123        | Admin              |
| ahmed.raza       | sales123        | Sales              |
| mehak.siddiqui   | inventory123    | Inventory Manager  |

## 5. Run the app

```bash
streamlit run app.py
```

It'll open at `http://localhost:8501`.

## Project structure

```
app.py                    -> Login screen / entry point
auth.py                   -> Login checking + password hashing
db.py                     -> All MySQL connection/query logic
style.py                  -> Shared CSS theme (cream/maroon/gold)
pages/
  1_Dashboard.py          -> Revenue, charts, low stock alerts
  2_Products.py           -> Search/filter products, add, restock
  3_Orders.py              -> Search/filter orders, view items, create order
  4_Customers.py           -> Search customers, add new customer
  5_Employees.py           -> Admin only: manage staff accounts
setup_demo_passwords.py   -> One-time script to set real demo passwords
requirements.txt
```

## Role permissions

| Action                  | Admin | Sales | Inventory Manager |
|--------------------------|:-----:|:-----:|:------------------:|
| View Dashboard            | ✅    | ✅    | ✅                 |
| View Products/Orders/Customers | ✅ | ✅  | ✅                 |
| Create Orders              | ✅    | ✅    | ❌                 |
| Add Customers               | ✅    | ✅    | ❌                 |
| Add/Restock Products        | ✅    | ❌    | ✅                 |
| Manage Employees             | ✅    | ❌    | ❌                 |

## Notes

- New orders go through the `sp_process_secure_checkout` stored procedure
  in your database — it locks the product row, checks stock, inserts the
  order + order item, and deducts stock, all atomically.
- Stock changes are automatically logged to `Stock_Change_Log` by a
  MySQL trigger — you don't need any Python code for that.
- All data lives in MySQL, not in Streamlit. Closing/restarting the app
  never loses data — it just re-reads whatever's currently in the database.
