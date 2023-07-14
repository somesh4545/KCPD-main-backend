## Installation

1. Clone the repository:

   `git clone <repository-url>`

2. Change into the project directory:

   `cd fastapi-mysql-sqlalchemy`

3. Install the required dependencies:

   `pip install -r requirements.txt`

4. Configure the database:

- Update the database connection details in the `config/db.py` file.
- Create a MySQL database and ensure the connection details are correct.

5. Run the application:

   `uvicorn index:app --reload`

The backend server should now be running on `http://localhost:8000`.

## API Documentation

The API documentation is automatically generated and available at `http://localhost:8000/docs`. It provides detailed information about the available endpoints, request/response formats, and authentication requirements.

## Database Schema

The database schema for the application can be found in the `models/index.py` file. It defines the tables and relationships used by SQLAlchemy to interact with the database.

## Contributing

Contributions to the project are welcome! If you find any issues or would like to add new features, please submit a pull request.
