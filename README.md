# URL Shortener API Documentation

## Overview

This project is a URL shortener API built with FastAPI, SQLAlchemy, and Redis. It allows users to shorten long URLs, manage their shortened URLs, and track access counts. The API provides user authentication and authorization to ensure that only authenticated users can create and manage their URLs.

## Technologies Used

-   **FastAPI**
-   **SQLAlchemy**
-   **PostgreSQL**
-   **Redis**
-   **Pydantic**
-   **Docker**

## API Endpoints

### 1. Authentication

#### 1.1 Register User

-   **Endpoint**: `/api/v1/auth/register`
-   **Method**: POST
-   **Description**: Registers a new user.
-   **Request Body**:

    ```json
    {
    "username": "string",
    "email": "string",
    "password": "string"
    }
    ```

-   **Response Body**:

    ```json
    {
    "id": 0,
    "username": "string",
    "email": "string",
    "created_at": "2024-10-26T14:30:00.000Z"
    }
    ```

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: POST /api/v1/auth/register
    API->>Database: Create User
    Database-->>API: User Data
    API-->>Client: User Response
    ```

#### 1.2 Login for Access Token

-   **Endpoint**: `/api/v1/auth/token`
-   **Method**: POST
-   **Description**: Logs in a user and returns an access token.
-   **Request Body**: `OAuth2PasswordRequestForm` (username and password)
-   **Response Body**:

    ```json
    {
    "access_token": "string",
    "token_type": "bearer"
    }
    ```

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: POST /api/v1/auth/token
    API->>Database: Authenticate User
    Database-->>API: User Data
    API->>API: Create Access Token
    API-->>Client: Token Response
    ```

### 2. URL Management

#### 2.1 Create Short URL

-   **Endpoint**: `/api/v1/urls/shorten`
-   **Method**: POST
-   **Description**: Creates a shortened URL for the provided original URL.
-   **Request Body**:

    ```json
    {
    "original_url": "string",
    "expires_in_days": 7
    }
    ```

-   **Response Body**:

    ```json
    {
    "original_url": "string",
    "short_url": "string",
    "expires_at": "2024-10-26T14:30:00.000Z",
    "created_at": "2024-10-19T14:30:00.000Z",
    "access_count": 0
    }
    ```

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: POST /api/v1/urls/shorten
    API->>Database: Create Short URL
    Database-->>API: URL Data
    API->>Redis: Store URL Data
    Redis-->>API: OK
    API-->>Client: URL Response
    ```

#### 2.2 Redirect to Original URL

-   **Endpoint**: `/{short_code}`
-   **Method**: GET
-   **Description**: Redirects to the original URL based on the provided short code.
-   **Path Parameter**: `short_code` (string)
-   **Response**: Redirect (307 Temporary Redirect)

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: GET /{short_code}
    API->>Redis: Get URL from Cache
    alt Cache Hit
    Redis-->>API: Original URL
    else Cache Miss
    API->>Database: Get URL from DB
    Database-->>API: Original URL
    API->>Redis: Store URL in Cache
    Redis-->>API: OK
    end
    API-->>Client: Redirect to Original URL
    ```

#### 2.3 Get URL Info

-   **Endpoint**: `/api/v1/urls/info/{short_code}`
-   **Method**: GET
-   **Description**: Retrieves information about a shortened URL.
-   **Path Parameter**: `short_code` (string)
-   **Response Body**:

    ```json
    {
    "original_url": "string",
    "short_code": "string",
    "short_url": "string",
    "expires_at": "2024-10-26T14:30:00.000Z",
    "created_at": "2024-10-19T14:30:00.000Z",
    "access_count": 0
    }
    ```

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: GET /api/v1/urls/info/{short_code}
    API->>Database: Get URL Info
    Database-->>API: URL Info
    API-->>Client: URL Info Response
    ```

#### 2.4 Get User URLs

-   **Endpoint**: `/api/v1/urls/urls/me`
-   **Method**: GET
-   **Description**: Retrieves all shortened URLs for the current user.
-   **Query Parameters**:
    -   `skip` (integer, default: 0): Number of records to skip.
    -   `limit` (integer, default: 100): Maximum number of records to retrieve.
-   **Response Body**:

    ```json
    [
    {
    "original_url": "string",
    "short_code": "string",
    "short_url": "string",
    "expires_at": "2024-10-26T14:30:00.000Z",
    "created_at": "2024-10-19T14:30:00.000Z",
    "access_count": 0
    }
    ]
    ```

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: GET /api/v1/urls/urls/me
    API->>Database: Get User URLs
    Database-->>API: URL List
    API-->>Client: URL List Response
    ```

### 3. Health Check

#### 3.1 Health Check

-   **Endpoint**: `/health`
-   **Method**: GET
-   **Description**: Checks the health status of the API, including the Redis and database connections.
-   **Response Body**:

    ```json
    {
    "status": "healthy",
    "redis": "connected",
    "database": "connected"
    }
    ```

-   **Mermaid Diagram**:

    ```mermaid
    sequenceDiagram
    Client->>API: GET /health
    API->>Redis: Ping Redis
    Redis-->>API: PONG
    API->>Database: SELECT 1
    Database-->>API: 1
    API-->>Client: Health Status Response
    ```

## Error Handling

The API returns standard HTTP status codes for errors:

-   **400 Bad Request**: Invalid request data.
-   **401 Unauthorized**: Authentication required.
-   **403 Forbidden**: User does not have permission.
-   **404 Not Found**: Resource not found.
-   **500 Internal Server Error**: An unexpected error occurred.

## Getting Started

1.  Clone the repository.
2.  Install requirements.
3.  Run the application using Docker.
4.  Start postgres and redis : 
    ```python
    sudo systemctl start postgresql
    sudo systemctl start redis
    ```
5.  For local hosting run : `uvicorn app.main:app --reload`
6.  Access the API documentation at `/api/v1/openapi.json`.
