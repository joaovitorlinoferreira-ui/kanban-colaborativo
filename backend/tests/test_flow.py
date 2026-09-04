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

@pytest.fixture
def created_board(user_tokens):
    headers_a = user_tokens["headers_a"]
    res_board = client.post("/boards/boards/", json={"title": "Projeto Teste"}, headers=headers_a)
    assert res_board.status_code in (200, 201), f"Erro ao criar board: {res_board.text}"
    board_data = res_board.json()
    board_id = board_data.get("id")

    res_get_board = client.get(f"/boards/boards/{board_id}", headers=headers_a)
    assert res_get_board.status_code == 200
    return res_get_board.json()

@pytest.fixture
def created_card(user_tokens, created_board):
    headers_a = user_tokens["headers_a"]
    columns = created_board.get("columns", [])
    assert len(columns) > 0, "O board precisa ter pelo menos uma coluna para criar card"
    
    col_id_1 = columns[0]["id"]
    res_card = client.post(
        f"/cards/column/{col_id_1}",
        json={"title": "Novo Card", "description": "Teste"},
        headers=headers_a
    )
    assert res_card.status_code in (200, 201), f"Erro ao criar card: {res_card.text}"
    return res_card.json(), created_board


# --- TESTES ATÔMICOS ---

def test_register_and_login(user_tokens):
    """Garante que o registro e login dos usuários A e B ocorrem com sucesso."""
    assert "headers_a" in user_tokens
    assert "headers_b" in user_tokens
    assert user_tokens["headers_a"]["Authorization"].startswith("Bearer ")
    assert user_tokens["headers_b"]["Authorization"].startswith("Bearer ")

def test_create_board_creates_default_columns(created_board):
    """Verifica se a criação de um board gera o board e suas colunas padrão."""
    assert created_board.get("title") == "Projeto Teste"
    columns = created_board.get("columns", [])
    assert isinstance(columns, list)
    assert len(columns) > 0

def test_create_card(created_card):
    """Valida a criação de um card em uma coluna do board."""
    card_data, _ = created_card
    assert card_data.get("title") == "Novo Card"
    assert card_data.get("description") == "Teste"
    assert "id" in card_data

def test_move_card(user_tokens, created_card):
    """Testa a movimentação bem-sucedida de um card por parte do dono do board."""
    headers_a = user_tokens["headers_a"]
    card_data, board_detail = created_card
    card_id = card_data.get("id")
    columns = board_detail.get("columns", [])

    col_id_2 = columns[1]["id"] if len(columns) > 1 else columns[0]["id"]

    move_payload = {
        "target_column_id": col_id_2,
        "new_order": 0
    }

    res_move = client.put(
        f"/cards/{card_id}/move",
        json=move_payload,
        headers=headers_a
    )
    assert res_move.status_code == 200, f"Erro ao mover card: {res_move.text}"

def test_move_card_forbidden_for_non_member(user_tokens, created_card):
    """Garante que um usuário sem permissão no board recebe HTTP 403 ao tentar mover um card."""
    headers_b = user_tokens["headers_b"]
    card_data, board_detail = created_card
    card_id = card_data.get("id")
    columns = board_detail.get("columns", [])

    col_id_2 = columns[1]["id"] if len(columns) > 1 else columns[0]["id"]

    move_payload = {
        "target_column_id": col_id_2,
        "new_order": 0
    }

    res_unauthorized = client.put(
        f"/cards/{card_id}/move",
        json=move_payload,
        headers=headers_b
    )
    assert res_unauthorized.status_code == 403, f"Acesso não autorizado deveria retornar 403: {res_unauthorized.text}"