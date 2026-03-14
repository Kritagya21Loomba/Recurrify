import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_parse_endpoint(client: AsyncClient):
    resp = await client.post("/parse", json={"input": "T(n) = 2T(n/2) + n"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["recurrence_type"] == "divide_and_conquer"
    assert "Master Theorem" in data["applicable_methods"]


@pytest.mark.anyio
async def test_solve_divide_and_conquer(client: AsyncClient):
    resp = await client.post("/solve", json={"input": "T(n) = 2T(n/2) + n"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["input"] == "T(n) = 2T(n/2) + n"
    assert len(data["solutions"]) > 0
    # Should have Master Theorem solution
    master = next((s for s in data["solutions"] if s["method"] == "Master Theorem"), None)
    assert master is not None
    assert master["applicable"] is True
    assert len(master["steps"]) >= 3
    assert "\\Theta" in master["closed_form"]


@pytest.mark.anyio
async def test_solve_linear(client: AsyncClient):
    resp = await client.post(
        "/solve",
        json={"input": "T(n) = T(n-1) + n", "base_cases": {"1": 1}},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["solutions"]) > 0


@pytest.mark.anyio
async def test_solve_fibonacci(client: AsyncClient):
    resp = await client.post(
        "/solve",
        json={"input": "T(n) = T(n-1) + T(n-2)", "base_cases": {"0": 0, "1": 1}},
    )
    assert resp.status_code == 200
    data = resp.json()
    char = next(
        (s for s in data["solutions"] if s["method"] == "Characteristic Equation"),
        None,
    )
    assert char is not None
    assert char["applicable"] is True


@pytest.mark.anyio
async def test_solve_with_verification(client: AsyncClient):
    resp = await client.post(
        "/solve",
        json={"input": "T(n) = 2T(n/2) + n", "base_cases": {"1": 1}},
    )
    assert resp.status_code == 200
    data = resp.json()
    master = next((s for s in data["solutions"] if s["method"] == "Master Theorem"), None)
    assert master is not None
    assert master["verification"] is not None
    assert len(master["verification"]["numeric_checks"]) > 0


@pytest.mark.anyio
async def test_solve_invalid_input(client: AsyncClient):
    resp = await client.post("/solve", json={"input": "not a recurrence"})
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_guided_flow(client: AsyncClient):
    # Start guided session
    resp = await client.post("/guided/start", json={"input": "T(n) = 2T(n/2) + n"})
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]
    assert data["total_questions"] > 0
    assert data["first_question"]["question_id"] == "q1_form"

    # Answer first question (multiple choice — pick the divide-and-conquer option)
    resp = await client.post(
        f"/guided/{session_id}/answer",
        json={"answer": "Divide-and-conquer: T(n) = aT(n/b) + f(n)"},
    )
    assert resp.status_code == 200
    fb = resp.json()["feedback"]
    assert fb["correct"] is True


@pytest.mark.anyio
async def test_guided_invalid_session(client: AsyncClient):
    resp = await client.post(
        "/guided/nonexistent/answer",
        json={"answer": "test"},
    )
    assert resp.status_code == 404
