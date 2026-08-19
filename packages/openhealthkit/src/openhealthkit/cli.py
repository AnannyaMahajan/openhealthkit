import uvicorn

from openhealthkit.config import settings


def main():
    """CLI entrypoint for running the OpenHealthKit server."""
    print("Starting OpenHealthKit Server...")
    uvicorn.run(
        "openhealthkit.main:app",
        host="0.0.0.0",
        port=8000,
        reload=(settings.ENV_MODE == "development"),
    )


if __name__ == "__main__":
    main()
