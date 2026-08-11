import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

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

    @patch("app.api.routes.products.new_client")
    def test_product_image_proxies_an_allowed_image(self, new_client) -> None:
        upstream = MagicMock(
            content=b"image-content",
            headers={"content-type": "image/jpeg"},
        )
        client = MagicMock()
        client.get = AsyncMock(return_value=upstream)
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        new_client.return_value = client

        url = "https://cdn-consum.aktiosdigitalservices.com/product.jpg"
        response = self.client.get("/product-image", params={"url": url})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"image-content")
        self.assertEqual(response.headers["content-type"], "image/jpeg")
        client.get.assert_awaited_once_with(url)

    @patch("app.api.routes.products.new_client")
    def test_product_image_rejects_unsupported_host(self, new_client) -> None:
        response = self.client.get(
            "/product-image", params={"url": "https://example.com/product.jpg"}
        )

        self.assertEqual(response.status_code, 400)
        new_client.assert_not_called()
