# Library Service Project

This is a Django REST Framework (DRF) project that implements a library service. The project features CRUD functionality for books and users, borrowing functionalities, JWT token authentication, and Docker support for easy deployment.
## Features
### Books Service
- CRUD functionality for books.
- Only admin users can create, update, and delete books.
- All users can list books, including unauthenticated users.
- JWT token authentication for user services.

### Users Service
- CRUD functionality for users.
- User model with email support.
- JWT token authentication.

### Borrowing Service
- CRUD functionality for borrowings.
- Constraints on borrow dates.
- Return borrowing functionality.
- Filtering for borrowings based on active status and user ID.
- Non-admin users can see only their borrowings.


### Docker Support
- Docker configuration for easy setup and deployment.
- Instructions for building and running the Docker container.


## Installation
### Steps:
#### 1. Clone the repository
```
git clone https://github.com/mish-sk/library-service-project
cd library-service-project
```

#### 2. Create and activate virtual environment
```
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
```

#### 3. Install dependencies
```
pip install -r requirements.txt
```

#### 4. Build the Docker image
```
docker-compose build
```

#### 5. Run the Docker container
```
docker-compose up
```

#### 6. Create a superuser in Docker
#### Get the container ID of the running container:
```
docker ps
```

#### Access the container:
```
docker exec -it <container_id> /bin/bash
```

#### Inside the container, create the superuser:
```
python manage.py createsuperuser
```

## License

This project is licensed under the MIT License.

---
