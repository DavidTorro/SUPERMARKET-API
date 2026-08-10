import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SUPERMARKET_API_SCRAPE_TOKEN", "test-scrape-token")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.schemas.product import Product, ProductPage  # noqa: E402


class ProductRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    @patch("app.api.routes.products.catalog_service.get_products")
    def test_products_forwards_filters_and_returns_page(self, get_products) -> None:
        get_products.return_value = ProductPage(
            total=1,
            page=2,
            page_size=25,
            pages=1,
            items=[
                Product(
                    id="123",
                    supermarket="mercadona",
                    name="Aceite de oliva",
                )
            ],
        )

        response = self.client.get(
            "/products",
            params={
                "supermarket": "mercadona",
                "q": "aceite",
                "category": "Aceites",
                "page": 2,
                "page_size": 25,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["name"], "Aceite de oliva")
        get_products.assert_called_once_with("mercadona", "aceite", "Aceites", 2, 25)

    @patch("app.api.routes.products.catalog_service.get_products")
    def test_products_rejects_unknown_supermarket(self, get_products) -> None:
        response = self.client.get("/products", params={"supermarket": "unknown"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Supermarket not found: unknown")
        get_products.assert_not_called()
