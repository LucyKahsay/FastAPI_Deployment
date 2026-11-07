# FastAPI Blog Application

A full-stack blog application built with **Python and FastAPI**, demonstrating practical backend engineering skills through REST API development, asynchronous database operations, authentication, automated testing, cloud storage integration, Docker containerization, and cloud deployment.

The project includes a browser-based interface and a REST API backed by PostgreSQL.

## Live Application

- **Live Demo:** [FastAPI Blog Application](https://fastapi-deployment-14l3.onrender.com)
- **API Documentation:** [Interactive Swagger UI](https://fastapi-deployment-14l3.onrender.com/docs)
- **Health Check:** [Application Health](https://fastapi-deployment-14l3.onrender.com/health)

**Current deployment:** Render using Docker, with Neon PostgreSQL for database hosting and Amazon S3 for profile image storage.

## Features

### User Management and Authentication
- User registration and login.
- JWT-based authentication.
- Password hashing and verification.
- Protected API endpoints.
- Password-reset functionality with token expiration.

### Blog Management
- Create, read, update, and delete blog posts.
- Authenticated post creation.
- Authorization checks to ensure users can only modify their own posts.
- Paginated blog post listings.
- Post-author relationships.

### Profile Image Management
- Profile picture uploads.
- Image validation and processing using Pillow.
- Image resizing and orientation correction.
- Support for JPEG, PNG, GIF, and WebP images.
- Amazon S3 integration for cloud-based image storage.
- Upload size validation.

### Database Management
- PostgreSQL integration.
- Asynchronous database operations using SQLAlchemy.
- Database schema management with Alembic.
- Database relationships and queries.

### Automated Testing
- API testing using pytest and HTTPX.
- Database test fixtures and dependency overrides.
- AWS service mocking with Moto.
- Mocking asynchronous functions during testing.

### Security and Deployment
- Environment-based configuration and secret management.
- Security headers middleware.
- Docker multi-stage builds.
- Non-root container execution.
- Docker image and container management.
- Application health-check endpoint.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL, Neon |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Authentication | JWT, password hashing |
| Cloud Storage | Amazon S3, Boto3 |
| Image Processing | Pillow |
| Testing | pytest, HTTPX, Moto |
| Containerization | Docker |
| Cloud Platforms | AWS EC2, Render |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Configuration | Pydantic Settings, environment variables |
| Development Tools | Git, GitHub, Linux |

## Deployment

The application has been deployed using two different cloud deployment approaches.

### 1. AWS EC2 — Virtual Machine Deployment

Deployed the FastAPI application on an **Amazon EC2 virtual machine**.

This deployment provided practical experience with:

- Cloud-based virtual machine hosting.
- Linux server administration.
- Remote server access and application configuration.
- Running a FastAPI application in a cloud environment.
- Configuring application and database connectivity.

### 2. Render — Docker Containerized Deployment

Deployed the application on **Render using Docker**.

This deployment involved:

- Creating a multi-stage Dockerfile.
- Building Docker images and running containers.
- Using a dedicated non-root user inside the container.
- Managing environment variables through the hosting platform.
- Connecting the containerized application to Neon PostgreSQL.
- Integrating Amazon S3 for profile image storage.
- Configuring an application health-check endpoint.
- Deploying automatically from the GitHub repository.

**Live application:** https://fastapi-deployment-14l3.onrender.com

**Interactive API documentation:** https://fastapi-deployment-14l3.onrender.com/docs

These two deployments demonstrate experience with both traditional virtual machine hosting and containerized cloud application deployment.

## Running Locally

### Prerequisites

- Python 3.14 or a compatible Python version.
- PostgreSQL database.
- Git.
- AWS S3 credentials if testing profile image uploads.

### 1. Clone the repository


git clone https://github.com/LucyKahsay/FastAPI_Deployment.git
cd FastAPI_Deployment


### 2. Create and activate a virtual environment


python -m venv .venv
source .venv/bin/activate


### 3. Install dependencies


pip install -r requirements.txt


### 4. Configure environment variables

Create a .env file in the project root and configure the required application settings.

These include:

- Database connection details.
- JWT secret key.
- AWS S3 bucket and region.
- AWS credentials, where required.
- Email configuration.

**Never commit your .env file or expose credentials in your repository.**

### 5. Run database migrations


alembic upgrade head


### 6. Start the application


fastapi dev main.py


The application will be available at:


http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs


## Running with Docker

### Build the Docker image

docker build -t fastapi-app .

### Run the container

docker run --rm \
  --name fastapi-blog \
  --env-file .env \
  -p 8080:8080 \
  fastapi-app

The application will be available at:

http://localhost:8080

## Running Tests

Run the automated test suite using:

pytest test

The test suite uses pytest, HTTPX, database fixtures, and Moto to test API functionality and mock AWS services.

## Security

The application incorporates several security practices:

- JWT-based authentication.
- Password hashing.
- Protected endpoints and authorization checks.
- Environment-based secret management.
- File type and upload size validation.
- Security response headers.
- Non-root Docker container execution.

Sensitive information such as database credentials, JWT secrets, and AWS access keys must be stored securely and excluded from version control.

## Skills Demonstrated

- Designing and developing RESTful APIs.
- Building asynchronous backend applications.
- Working with relational databases and ORM models.
- Implementing authentication and authorization.
- Managing database schemas and migrations.
- Writing automated API tests.
- Debugging application and integration issues.
- Integrating external cloud services.
- Building and deploying Docker containers.
- Deploying applications to AWS EC2 and Render.
- Working with Git, GitHub, and Linux.
- Configuring production application environments.

## Project Status

**Currently deployed and accessible through Render.**

The project demonstrates practical experience in backend development, database management, authentication, automated testing, cloud integration, containerization, and deployment.
