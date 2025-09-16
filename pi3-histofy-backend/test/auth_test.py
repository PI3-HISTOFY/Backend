import pytest
from httpx import AsyncClient
from app.main import app

# 🔹 Cliente de prueba
@pytest.mark.asyncio
async def test_register_user():
    """
    Caso: Registrar un nuevo usuario
    Esperado: 201 Created
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_correct_credentials():
    """
    Caso: Login con credenciales correctas
    Esperado: 200 OK y token JWT
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]


@pytest.mark.asyncio
async def test_login_incorrect_credentials():
    """
    Caso: Login con credenciales incorrectas
    Esperado: 401 Unauthorized
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token():
    """
    Caso: Acceder a endpoint protegido sin token
    Esperado: 401 Unauthorized
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/me")  # <- Ajusta si tu ruta protegida es distinta
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_token():
    """
    Caso: Acceder a endpoint protegido con token válido
    Esperado: 200 OK con datos del usuario
    """
    # Primero, obtener el token de login correcto
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login = await ac.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword"
        })
        token = login.json()["access_token"]

        # Usar el token en la cabecera
        response = await ac.get(
            "/users/me",  # <- Ajusta si tu ruta protegida es distinta
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
