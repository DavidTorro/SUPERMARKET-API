import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SUPERMARKET_API_SCRAPE_TOKEN", "test-scrape-token")

from fastapi.testclient import TestClient  # noqa: E402
from pydantic import SecretStr  # noqa: E402

from app.api.routes import scrape as scrape_routes  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas.product import ScrapeJob  # noqa: E402


class ScrapeRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    def test_scrape_requires_a_valid_token(self) -> None:
        with patch.object(
            scrape_routes.settings, "scrape_token", SecretStr("test-scrape-token")
        ):
            missing_token = self.client.post("/scrape/mercadona")
            invalid_token = self.client.post(
                "/scrape/mercadona", headers={"X-Scrape-Token": "invalid"}
            )

        self.assertEqual(missing_token.status_code, 401)
        self.assertEqual(invalid_token.status_code, 401)

    @patch("app.api.routes.scrape.scrape_service.start_job")
    def test_scrape_starts_job_with_valid_token(self, start_job) -> None:
        start_job.return_value = ScrapeJob(supermarket="mercadona", status="running")

        with patch.object(
            scrape_routes.settings, "scrape_token", SecretStr("test-scrape-token")
        ):
            response = self.client.post(
                "/scrape/mercadona",
                headers={"X-Scrape-Token": "test-scrape-token"},
            )

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["status"], "running")
        start_job.assert_called_once_with("mercadona")
