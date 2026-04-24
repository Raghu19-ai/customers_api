# Customer Management System API

A backend application built using FastAPI with authentication, role-based access control, logging, and CSV upload support.



## Features

* JWT Authentication (Login and Register)
* Role-Based Access Control (User, Admin, Superadmin)
* Customer and Address Management
* CSV Upload for bulk data
* Pagination support
* Rate limiting
* Logging with correlation ID
* CORS enabled for frontend integration



# Project Structure

customer_api/

backend/
    main.py
    database/
    models/
    schemas/
    routers/
    services/
    utils/
    app.log

frontend/
    index.html
    css/
    js/

requirements.txt



# Setup Instructions

1. Clone the project

git clone <your-repo-url>
cd customer_api


2. Create virtual environment


python -m venv env
env\Scripts\activate


3. Install dependencies

pip install -r requirements.txt


4. Run backend server

uvicorn backend.main:app --reload


5. Open frontend

Open the file:

frontend/index.html




#API Endpoints

Auth:

* POST /auth/register
* POST /auth/login
* POST /auth/refresh

Customers:

* GET /customers
* POST /customers
* PUT /customers/{id}
* DELETE /customers/{id}

Addresses:

* POST /addresses
* GET /addresses

---

## Roles and Permissions

User:

* Read access

Admin:

* Create and update access

Superadmin:

* Full access including delete, upload, and user management



# Logging

* Rotating log files (5MB size, 3 backups)
* Correlation ID for request tracking
* Logs stored in app.log



# Tech Stack

* FastAPI
* SQLAlchemy
* PostgreSQL
* JavaScript
* HTML and CSS



# Future Improvements

* Docker deployment
* Redis caching
* API monitoring
* Role management UI



