"""Development entry point for recAPI."""

from . import create_app


def main():
    """Run the Flask development server using configured host and port."""
    app = create_app()
    app.run(
        debug=app.config.get("DEBUG", False),
        host=app.config.get("WSGI_HOST", "127.0.0.1"),
        port=app.config.get("WSGI_PORT", 9005),
    )


if __name__ == "__main__":
    main()
