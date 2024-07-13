# Splitwise API

A FastAPI-based REST API for expense sharing and group management, similar to Splitwise.



## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Live Documentation](#live-documentation)
- [Setup and Installation](#setup-and-installation)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Database](#database)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Features

- User registration and authentication
- Group creation and management
- Expense tracking and splitting
- Multiple expense split types (equal, percentage, fixed)
- Balance calculation
- Debt simplification for settling group expenses

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints.
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management using Python type annotations.
- [Jose](https://python-jose.readthedocs.io/en/latest/): JavaScript Object Signing and Encryption (JOSE) implementation in Python for JWT.
- [Passlib](https://passlib.readthedocs.io/en/stable/): Password hashing library.
- [Deta](https://www.deta.sh/): Cloud database service for storing user, group, and expense data.
- [Python-dotenv](https://github.com/theskumar/python-dotenv): Reads key-value pairs from a .env file and sets them as environment variables.

## Project Structure

```
splitwise-api/
├── main.py
├── config.py
├── database.py
├── auth.py
├── utils.py
├── routers/
│   ├── users.py
│   ├── groups.py
│   └── expenses.py
├── requirements.txt
└── .env
```
## Live Documentation

The API documentation is hosted and can be accessed at:

[https://splitwise-1-f4819326.deta.app/docs](https://splitwise-1-f4819326.deta.app/docs)

This interactive documentation provides detailed information about all available endpoints, request/response schemas, and allows you to test the API directly from your browser.

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/splitwise-api.git
   cd splitwise-api
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add the following environment variables:
   ```
   SPLITWISE_PROJECT_KEY=your_deta_project_key
   SECRET_KEY=your_secret_key_for_jwt
   ```

5. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## API Endpoints

### Users

- `POST /users/register`: Register a new user
- `POST /users/login`: Login and receive an access token
- `GET /users/me`: Get current user's profile
- `PUT /users/me`: Update current user's profile
- `DELETE /users/me`: Delete current user's account

### Groups

- `POST /groups/`: Create a new group
- `GET /groups/`: Get all groups for the current user
- `GET /groups/{group_id}`: Get a specific group
- `PUT /groups/{group_id}`: Update a group
- `DELETE /groups/{group_id}`: Delete a group
- `POST /groups/{group_id}/members/{username}`: Add a member to a group
- `DELETE /groups/{group_id}/members/{username}`: Remove a member from a group

### Expenses

- `POST /expenses/`: Create a new expense
- `GET /expenses/{group_id}`: Get all expenses for a group
- `GET /expenses/{group_id}/{expense_id}`: Get a specific expense
- `PUT /expenses/{group_id}/{expense_id}`: Update an expense
- `DELETE /expenses/{group_id}/{expense_id}`: Delete an expense
- `GET /expenses/{group_id}/balances`: Get balances for a group
- `GET /expenses/user/balances`: Get balances for the current user across all groups
- `POST /expenses/{group_id}/settle`: Settle debts for a group

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, you need to include the JWT token in the Authorization header of your requests:

```
Authorization: Bearer <your_access_token>
```

## Database

This project uses Deta as the database. The database structure consists of three main collections:

1. `splitwise_users`: Stores user information
2. `splitwise_groups`: Stores group information
3. `splitwise_expenses`: Stores expense information

## Error Handling

The API uses standard HTTP status codes for error responses. Common error codes include:

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Detailed error messages are provided in the response body.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.