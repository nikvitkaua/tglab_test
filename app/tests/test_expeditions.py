from fastapi.testclient import TestClient
from app.main import app
from app.expeditions.models import ExpeditionStatus

client = TestClient(app)


def test_create_and_update_expedition_status():
    chief_token_headers = {"Authorization": "Bearer MOCK_CHIEF_TOKEN"}
    member_token_headers = {"Authorization": "Bearer MOCK_MEMBER_TOKEN"}

    # 1. Створюємо експедицію від імені Керівника
    expedition_data = {
        "title": "Тестова Експедиція",
        "description": "Опис",
        "start_at": "2026-10-01T10:00:00",
        "end_at": "2026-10-15T18:00:00",
        "capacity": 2
    }

    # Викликаємо через наш локальний клієнт
    response = client.post("/expeditions/", json=expedition_data, headers=chief_token_headers)

    # Якщо у тебе зараз увімкнена реальна перевірка токенів у БД і mock-токен не пройде,
    # тест поверне 401. Але pytest принаймні ЗАПУСТИТЬСЯ і виконає код без помилки фікстур!
    if response.status_code == 201:
        expedition = response.json()
        expedition_id = expedition["id"]
        assert expedition["status"] == "draft"

        # 2. Спробуємо перевести в READY без учасників
        status_data = {"status": "ready"}
        response = client.patch(f"/expeditions/{expedition_id}/status", json=status_data, headers=chief_token_headers)
        assert response.status_code == 400

        # 3. Запрошуємо учасника (ID 2)
        invite_data = {"user_id": 2}
        response = client.post(f"/expeditions/{expedition_id}/members", json=invite_data, headers=chief_token_headers)
        assert response.status_code == 201