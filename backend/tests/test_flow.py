import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def user_tokens():
    reg_a = {"email": "usera@test.com", "password": "password123", "name": "User A"}
    reg_b = {"email": "userb@test.com", "password": "password123", "name": "User B"}

    # Registra Usuários
    client.post("/auth/auth/register", json=reg_a)
    client.post("/auth/auth/register", json=reg_b)

    def get_token(email, password):
        res = client.post("/auth/auth/login", data={"username": email, "password": password})
        if res.status_code != 200:
            res = client.post("/auth/auth/login", json={"email": email, "password": password})
        
        if res.status_code != 200:
            raise RuntimeError(f"Erro no login ({res.status_code}): {res.text}")

        data = res.json()
        return data.get("access_token") or data.get("token")

    token_a = get_token("usera@test.com", "password123")
    token_b = get_token("userb@test.com", "password123")

    return {
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"}
    }

def test_full_kanban_flow(user_tokens):
    headers_a = user_tokens["headers_a"]
    headers_b = user_tokens["headers_b"]

    # 1. Usuário A cria um Board
    res_board = client.post("/boards/boards/", json={"title": "Projeto Teste"}, headers=headers_a)
    assert res_board.status_code in (200, 201), f"Erro ao criar board: {res_board.text}"
    board_data = res_board.json()
    board_id = board_data.get("id")

    # 2. Busca o Board para capturar as colunas
    res_get_board = client.get(f"/boards/boards/{board_id}", headers=headers_a)
    assert res_get_board.status_code == 200
    board_detail = res_get_board.json()
    
    columns = board_detail.get("columns", [])
    if columns:
        col_id_1 = columns[0]["id"]
        col_id_2 = columns[1]["id"] if len(columns) > 1 else col_id_1

        # 3. Criar Card
        res_card = client.post(
            f"/cards/column/{col_id_1}",
            json={"title": "Novo Card", "description": "Teste"},
            headers=headers_a
        )
        assert res_card.status_code in (200, 201), f"Erro ao criar card: {res_card.text}"
        card_id = res_card.json().get("id")

        # Payload exato exigido pela sua rota Pydantic
        move_payload = {
            "target_column_id": col_id_2,
            "new_order": 0
        }

        # 4. Mover Card (Dono do board)
        res_move = client.put(
            f"/cards/{card_id}/move",
            json=move_payload,
            headers=headers_a
        )
        assert res_move.status_code == 200, f"Erro 422/Move: {res_move.text}"

        # 5. Mover Card (Usuário sem permissão -> 403)
        res_unauthorized = client.put(
            f"/cards/{card_id}/move",
            json=move_payload,
            headers=headers_b
        )
        assert res_unauthorized.status_code == 403, f"Erro permissão: {res_unauthorized.text}"