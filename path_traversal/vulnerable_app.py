from pathlib import Path
from flask import Flask, abort, request, send_file

# Create the demo app with Flask's automatic static-file route disabled.
app = Flask(__name__, static_folder=None)

# Locate the project folder and the intended public downloads folder.
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"


@app.get("/")
def index():
    # Display a link for downloading a permitted public file.
    return '<h1>Vulnerable download demo</h1><a href="/download?filename=welcome.txt">Download welcome.txt</a>'


@app.get("/download")
def download():
    # Read the user-controlled filename from the URL query parameter.
    filename = request.args.get("filename", "")

    # Reject missing/empty filenames and null bytes.
    # These checks do not prevent path traversal.
    if not filename or "\x00" in filename:
        abort(400, description="A valid filename is required.")

    # VULNERABILITY: joining paths does not restrict access to downloads.
    # A filename such as ../private/confidential.txt escapes that folder.
    target = DOWNLOAD_DIR / filename

    # Confirm the target is a file, but do not check whether access is allowed.
    if not target.is_file():
        abort(404, description="File not found.")

    # Return the file as a download. Without a containment check, this
    # can disclose files outside downloads that the app has permission to read.
    return send_file(target, as_attachment=True)


if __name__ == "__main__":
    # Run the intentionally vulnerable demo locally with debugging disabled.
    app.run(host="127.0.0.1", port=5000, debug=False, load_dotenv=False)