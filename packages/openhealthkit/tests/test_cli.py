from unittest.mock import patch
import pytest
from openhealthkit.cli import main
from openhealthkit.config import settings


def test_cli_main_invokes_uvicorn():
    with patch("uvicorn.run") as mock_run:
        main()
        mock_run.assert_called_once_with(
            "openhealthkit.main:app",
            host="0.0.0.0",
            port=8000,
            reload=(settings.ENV_MODE == "development"),
        )


