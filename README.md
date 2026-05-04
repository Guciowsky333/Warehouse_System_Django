# The Warehouse System 

This project is based on a warehouse management system I use at my current job. 
I rebuilt it with improvements and new features — such as location weight validation — 
to make it more practical for real production use.

The system allows warehouse workers to manage component stock, track locations, 
release components by FIFO method, and maintain a full history of all warehouse operations.

The project is covered by 107 tests written in pytest.

---


## 🛠 Tech Stack

**Backend:**
- Django 5.2  
- Django REST Framework  
- PostgreSQL  
- Python 3.13
- SimpleJWT
- drf-spectacular (Swagger UI)

**Infrastructure:**  
- Docker  
- Docker Compose  
- Separate containers for `web` (Django) and `db` (PostgreSQL)

**Testing:**  
- pytest  
- pytest-django

**Code Quality:**
- ruff (linting & formatting)
- pre-commit hooks
- GitHub Actions (CI)

---

## ✨ Features

Each user in this project has a role that enable to do certain things.

**Allowed roles:**
- `warehouseman` — can perform basic warehouse operations (change location, release components, check stock)
- `foreman` — all warehouseman permissions + can create and manage lists
- `manager` — full access including creating users and accepting components from outside

This project consists of 4 django applications that are responsible for specific features.

**Applications:**

**history:**
- Shows a full history of all warehouse operations
- Each operation has its own action, allowed actions: `change_location`, `component_release`, `component_undo`
- Filter by component `code`, `unique_code` or `user_name`
- Pagination implemented, max page size = 10

**inventory:**
- Change location of a provided component
- Release component from warehouse to a provided department, allowed departments: `5000`, `5500`, `5800`, `6000`
- Track locations of components sorted by FIFO method
- Check components inside a provided location
- Check quantity of a component at stock or in a provided department
- Return components from department back to the warehouse
- Accept components from outside into the warehouse (manager role only)

**list_LPT:**
- Available for users with foreman role or higher only
- Create a list with ordered components assigned by FIFO method
- Release components from a provided list

**users:**
- Available for users with manager role only
- Create new users
- Reset password of a provided user by username

---





## 🚀 Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/Guciowsky333/Warehouse_System_Django

# 2. Create .env file (see Environment Variables section below)

# 3. Install pre-commit hooks
pre-commit install

# 4. Build and start Docker containers
docker-compose up --build

# 5. Create a superuser (Optional)
docker-compose exec web python manage.py createsuperuser
```

### Running tests
```bash
# Run all 107 tests 
docker-compose exec web pytest

# Run a single test
docker-compose exec web pytest -k "test_name"
```

---




## ⚙️ Environment Variables

Before running the project, create a .env file in the root directory.
Example configuration:

### Django
```
SECRET_KEY=your_secret_key
DEBUG=True
``` 

### PostgreSQL
```
POSTGRES_DB=warehouse_db
POSTGRES_USER=warehouse_user
POSTGRES_PASSWORD=warehouse_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## 🔎 Notes
- POSTGRES_HOST should match the database service name in docker-compose.yml (usually db)
- Do not use real credentials in public repositories

---




## 📚 API Documentation

After running the project, API documentation is available at:

### Swagger UI
http://localhost:8000/api/docs/

### OpenAPI Schema
http://localhost:8000/api/schema/

---



## 📁 Project Structure
```
Warehouse_System_Django/
│
├── users/ # User management (creation, password reset, roles)
├── inventory/ # Core warehouse logic (FIFO, stock, locations)
├── history/ # Full history of all warehouse operations
├── list_LPT/ # Creates lists and releases components from them
│
├── config/ # Django settings and project configuration
├── manage.py
│
├── docker-compose.yml
└── Dockerfile
```

---

### 👤 Author

**Kacper Kubiak**
- GitHub : [Warehouse_System](https://github.com/Guciowsky333/Warehouse_System_Django)
 


