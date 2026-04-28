# 🚗 Car Rental System

A full-stack web application for managing car rentals, built with **Django**.  
The project supports both **admin management** and **customer booking workflows**.

🌐 **Live Demo:**  
https://kp432030.pythonanywhere.com/

---

## ✨ Features

### 👤 Customer Side
- Register and log in
- Browse available cars
- Create rental orders
- View personal orders
- Pay for rentals using simulated Google Pay
- Pay repair fees if damage is detected
- Track order and payment status

### 🛠 Admin Side
- Add, edit and delete cars
- Manage car availability
- Approve or reject rental orders
- Register car returns
- Add damage reports
- Create repair invoices
- Track rental and repair payments

---

## 🔐 Demo Accounts

### Admin
Username: admin1  
Password: admin12345  

### Customer
Username: client1  
Password: client12345  

---

## 🚘 Car Statuses

- Available
- Reserved
- Rented
- Maintenance

---

## 📦 Order Workflow

Pending → Approved → Active → Returned → Closed  
↘ Rejected  
↘ Damage Pending → Repair Paid → Closed  

---

## 💳 Payments

The application includes a simulated payment flow:
- Rental payment
- Repair payment
- Google Pay-style confirmation page  

No real money is charged.

---

## 🖼 Screenshots

Add screenshots to a folder named **screenshots/** in your repository.

Example:

![Login](screenshots/login.png)
![Cars](screenshots/cars.png)
![Orders](screenshots/orders.png)

---

## 🛠 Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- PythonAnywhere

---

## ⚙️ Installation

```bash
git clone https://github.com/kate20031/CarRental2.git
cd CarRental2

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## 🌐 Deployment

Live: https://kp432030.pythonanywhere.com/

---

## 👩‍💻 Author

Kate Pavlichenko  
https://github.com/kate20031
