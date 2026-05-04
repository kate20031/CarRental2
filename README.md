#  Car Rental System

A web application for managing car rentals, built with **Django**.

The system supports separate workflows for **customers** and **administrators**: customers can browse available cars, create rental orders, pay for approved rentals, and pay repair invoices. Administrators can manage cars, approve or reject rental requests, register returns, and create repair invoices for damaged vehicles.

 **Live Demo:**  
https://kp432030.pythonanywhere.com/

---

##  Features

###  Customer Side

- Register and log in
- Browse available cars
- Create rental orders
- View personal orders
- Pay for approved rentals using a simulated Google Pay page
- View rejected orders and rejection reasons
- Pay repair fees if vehicle damage was registered by the administrator
- Track rental, payment, return, and repair statuses

###  Admin Side

- Add new cars
- Edit and delete cars
- Manage car availability through the order workflow
- Approve or reject rental orders
- Provide rejection reasons
- Register car returns
- Mark returned cars as damaged or undamaged
- Create repair invoices for damaged cars
- Track paid and unpaid repair invoices

---

##  Architecture

The project is implemented as a Django web application with server-rendered frontend pages and an additional **Django REST Framework backend API**.

The main user interface is built with Django templates, while core business entities are also exposed through JSON API endpoints protected by JWT authentication.

The system contains:

- **Frontend pages** for customers and administrators
- **Backend API endpoints** returning JSON
- **JWT authentication** for API access
- **Django ORM models** for database interaction
- **Django migrations** for database schema changes
- **Unit tests** for accounts, cars, and orders logic

Some frontend pages are rendered by Django templates, while the backend API layer can be tested independently through JWT-protected endpoints.

---

##  Demo Accounts

### Admin

```text
Username: admin2
Password: admin12345
```

### Customer

```text
Username: client5
Password: 12345
```


---

##  Car Statuses

- `available` — the car can be rented
- `reserved` — the car has an approved order but is not yet paid
- `rented` — the rental is paid and active

---

##  Order Workflow

```text
pending → approved → active → returned
   ↘ rejected
   ↘ damage_pending → repair paid → returned
```

### Status Meaning

- `pending` — customer created an order and waits for admin approval
- `approved` — admin approved the order; customer can pay
- `active` — rental is paid and car is currently rented
- `returned` — car was returned successfully
- `rejected` — admin rejected the order and added a reason
- `damage_pending` — car was returned with damage and customer must pay a repair invoice

---

##  Payments

The application includes a simulated payment flow:

- Rental payment
- Repair payment
- Google Pay-style confirmation page

No real money is charged. The payment page only imitates the payment confirmation process for educational purposes.

---

##  Repair Invoice Logic

If a car is returned with damage:

1. The administrator registers the damage.
2. A repair invoice is created.
3. The order receives the `damage_pending` status.
4. The customer pays the repair invoice.
5. After payment, the order becomes `returned` and the car becomes available again.

---

##  API Endpoints

The project includes a Django REST Framework API protected with JWT authentication.

### Auth

```http
POST /api/token/
POST /api/token/refresh/
```

### Cars

```http
GET    /api/cars/
POST   /api/cars/
GET    /api/cars/<id>/
PUT    /api/cars/<id>/
PATCH  /api/cars/<id>/
DELETE /api/cars/<id>/
```

### Orders

```http
GET  /api/orders/
POST /api/orders/
GET  /api/orders/my/
POST /api/orders/<id>/approve/
POST /api/orders/<id>/reject/
POST /api/orders/<id>/pay/
GET  /api/orders/returns/
POST /api/orders/returns/<id>/
```

---

##  API Authentication Example

### Obtain JWT Token

```http
POST /api/token/
Content-Type: application/json
```

```json
{
  "username": "admin2",
  "password": "admin12345"
}
```

Example response:

```json
{
  "refresh": "refresh_token_here",
  "access": "access_token_here"
}
```

### Protected API Request

```http
GET /api/cars/
Authorization: Bearer <access_token>
```

---

##  Testing

The project contains unit tests for the main applications:

```text
accounts/tests.py
cars/tests.py
orders/tests.py
```

Run all tests:

```bash
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test accounts
python manage.py test cars
python manage.py test orders
```

The tests cover:

- user registration and login
- profile creation
- JWT token creation
- car API access
- admin-only car management
- order creation
- order approval and rejection
- rental payment
- car return
- damage invoice creation
- repair payment workflow

---

##  OOP Usage

The project uses object-oriented programming through Django and Django REST Framework:

- models inherit from `models.Model`
- serializers inherit from `serializers.ModelSerializer`
- API views use DRF generic views and function-based API views
- custom permission classes implement role-based access control
- business entities are represented as classes: `Car`, `Order`, `DamageInvoice`, `Profile`

---

##  Logging

The project can be extended with Django logging for important business actions such as:

- order creation
- order approval
- order rejection
- rental payment
- car return
- repair invoice creation
- repair payment

Recommended logging configuration can be added to `settings.py` using Python's built-in `logging` module.

---

##  Screenshots

![Login](screenshots/login.png)

![Cars](screenshots/cars.png)

![Orders](screenshots/orders.png)

![Returns](screenshots/returns.png)

---

##  Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite / PostgreSQL
- Django ORM
- Django Migrations
- HTML
- CSS
- JavaScript
- Django Authentication
- PythonAnywhere

---

##  Installation

```bash
git clone https://github.com/kate20031/CarRental2.git
cd CarRental2

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Open the project locally:

```text
http://127.0.0.1:8000/
```

---

##  Creating an Admin User

```bash
python manage.py createsuperuser
```

After creating a superuser, log in through:

```text
http://127.0.0.1:8000/login/
```

Admin users are detected using Django's built-in `is_staff` field.

---

##  Creating Demo Users Locally

If the database is empty after cloning the project, create demo users manually:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

User.objects.create_superuser(
    username="admin2",
    email="admin2@test.com",
    password="admin12345"
)

User.objects.create_user(
    username="client5",
    password="12345"
)
```

If your project uses profiles for passport data, create a profile for the customer as well.

---

##  Git Ignore

The repository should include a `.gitignore` file to avoid committing local or generated files:

```gitignore
venv/
__pycache__/
*.pyc
.env
.idea/
db.sqlite3
*.log
```

---

##  Deployment

Live version:

https://kp432030.pythonanywhere.com/

The project is deployed on **PythonAnywhere**.

---

##  Main Project Structure

```text
CarRental2/
├── accounts/
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── cars/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── orders/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── templates/
│   ├── layouts/
│   ├── cars/
│   └── orders/
├── static/
│   └── style.css
├── screenshots/
│   ├── login.png
│   ├── cars.png
│   ├── orders.png
│   └── returns.png
├── config/
│   ├── settings.py
│   └── urls.py
├── requirements.txt
├── README.md
└── manage.py
```

---

##  Author

**Kate Pavlichenko**  
GitHub: https://github.com/kate20031
