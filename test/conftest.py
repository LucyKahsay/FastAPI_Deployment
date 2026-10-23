#The module provides tools for interacting 
# with the operating system.
import os 
from config import settings

from collections.abc import AsyncGenerator

# We use os.environ because Python needs 
# a way to interact with environment
# variables.
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://bloguser:MyStrongPassword123!@localhost/test_blog"
)
os.environ["S3_BUCKET_NAME"] = "test-bucket"
settings.s3_bucket_name = "test-bucket"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"


os.environ["S3_ACCESS_KEY_ID"] = "testing"
os.environ["S3_SECRET_ACCESS_KEY"] = "testing"
os.environ["S3_REGION"] = "eu-north-1"

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "eu-north-1"



import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app




# Think of pytest as a car. 
# AnyIO is an extra tool that 
# helps the car handle asynchronous testing.
# This line tells pytest: 
# "Load the AnyIO testing plugin."
pytest_plugins = ["anyio"]


# A fixture is a function that pytest
# can use to provide something a test needs.
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# The fixture returns the string "asyncio". 
# That value tells AnyIO which asynchronous
# system to use.


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
def mocked_aws():
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-north-1")
        s3.create_bucket(
            Bucket=os.environ["S3_BUCKET_NAME"],
            CreateBucketConfiguration={
                "LocationConstraint": "eu-north-1"
            },
        )

        
        yield s3




@pytest.fixture

# When a test runs, Pytest looks at this and says:
# "Ah, this test needs a clean, empty test database "
# "(db_session) and a fake version of AWS (mocked_aws)"
# " so we don't accidentally delete real data or get"
# " billed by Amazon." Pytest builds those safely 
# behind the scenes and hands them to this function.
async def client(
    db_session: AsyncSession,
    mocked_aws,
) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    
    # app.dependency_overrides is a built-in safety hatch 
    # in FastAPI. It says: "If anyone asks for get_db, "
    # "ignore the real one. Use override_get_db instead."
    # Because override_get_db is wired to yield your safe 
    # test db_session, your app is now tricked into running 
    # the test using the fake database.
    app.dependency_overrides[get_db] = override_get_db

    # AsyncClient sends HTTP requests to your app.
    # AsyncClient comes from HTTPX. It allows your 
    # test to send requests to your FastAPI 
    # application without necessarily 
    # starting a real web server.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()



async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}