from application import create_app


app = create_app()


# Run the application
if __name__ == "__main__":
    app.run(
        host = "127.0.0.1",
        port = 5001,
        debug = True
        )