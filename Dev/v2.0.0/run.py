from application import create_app, db
from flask import url_for, request

app = create_app()

@app.template_filter("url_in_url_list")
def url_in_url_list(url_list):
    if any([ request.path == url_for(url) for url in url_list ]):
        return True
    return False


if __name__ == "__main__":
    app.run(
        host = "127.0.0.1",
        port = 5001,
        debug = True
        )