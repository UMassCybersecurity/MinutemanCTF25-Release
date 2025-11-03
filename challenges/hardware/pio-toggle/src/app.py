# app.py
import os
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from adafruit_pioasm import assemble
import emulator  # must define TARGET_PIN, TARGET_TOGGLE_CYCLES, run_program(list[int]) -> bool

# Read flag from environment at startup (None if not set)
FLAG = os.environ.get("FLAG")

ALLOWED_EXTENSIONS = {"asm", "txt", "pio"}
MAX_FILE_SIZE = 16 * 1024  # 16 KB

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "214231575695753412643856987432")
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB upload limit

def allowed_filename(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        target_pin=getattr(emulator, "TARGET_PIN", None),
        target_cycles=getattr(emulator, "TARGET_TOGGLE_CYCLES", None),
        flag=None,  # never reveal flag on plain GET
    )


@app.route("/submit", methods=["POST"])
def submit():
    source = None

    # Try to read from textarea
    if "source" in request.form and request.form["source"].strip():
        source = request.form["source"].strip()
    # Try to read from file upload
    elif "file" in request.files:
        f = request.files["file"]
        if f and f.filename:
            filename = secure_filename(f.filename)
            if not allowed_filename(filename):
                flash("Invalid file type (.asm or .txt only).", "danger")
                return redirect(url_for("index"))

            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
            if size > MAX_FILE_SIZE:
                flash(f"File too large ({size} bytes). Limit {MAX_FILE_SIZE} bytes.", "danger")
                return redirect(url_for("index"))

            source = f.read().decode("utf-8", errors="replace")

    if not source:
        flash("No source code provided.", "danger")
        return redirect(url_for("index"))

    # Assemble user code
    try:
        opcodes = assemble(source)
    except Exception as e:
        app.logger.error("Assembly failed:\n%s", traceback.format_exc())
        flash(f"Assembly failed: {e}", "danger")
        return render_template(
            "index.html",
            assembly_error=str(e),
            source=source,
            target_pin=getattr(emulator, "TARGET_PIN", None),
            target_cycles=getattr(emulator, "TARGET_TOGGLE_CYCLES", None),
            flag=None,
        )

    # Run the emulator
    try:
        solved = emulator.run_program(list(opcodes))
    except Exception as e:
        app.logger.error("Emulator error:\n%s", traceback.format_exc())
        flash(f"Emulator execution failed: {e}", "danger")
        return render_template(
            "index.html",
            execution_error=str(e),
            source=source,
            target_pin=getattr(emulator, "TARGET_PIN", None),
            target_cycles=getattr(emulator, "TARGET_TOGGLE_CYCLES", None),
            flag=None,
        )

    if solved:
        # only show the flag when solved is True and FLAG is set
        if FLAG:
            flash("✅ Success! Here is your flag.", "success")
            revealed_flag = FLAG
        else:
            flash("✅ Success! (FLAG environment variable not set on server.)", "success")
            revealed_flag = None
    else:
        flash("❌ Incorrect output — your program didn't meet the target.", "warning")
        revealed_flag = None

    # Render page; pass flag into template only if revealed_flag is not None
    return render_template(
        "index.html",
        source=source,
        assembled=list(opcodes),
        target_pin=getattr(emulator, "TARGET_PIN", None),
        target_cycles=getattr(emulator, "TARGET_TOGGLE_CYCLES", None),
        flag=revealed_flag,
    )


@app.route("/api/submit", methods=["POST"])
def api_submit():
    """JSON API: POST { "source": "<pio asm>" } -> { ok, solved?, flag?, ... }"""
    data = request.get_json(force=True, silent=True)
    if not data or "source" not in data:
        return jsonify({"ok": False, "error": "Missing 'source'"}), 400

    source = data["source"]
    if not isinstance(source, str) or not source.strip():
        return jsonify({"ok": False, "error": "Invalid or empty 'source'"}), 400

    try:
        opcodes = assemble(source)
    except Exception as e:
        return jsonify({"ok": False, "stage": "assemble", "error": str(e)}), 400

    try:
        solved = emulator.run_program(list(opcodes))
    except Exception as e:
        return jsonify({"ok": False, "stage": "execute", "error": str(e)}), 500

    # Only include flag if solved and FLAG exists
    result = {
        "ok": True,
        "solved": bool(solved),
        "num_instructions": len(opcodes),
        "target_pin": getattr(emulator, "TARGET_PIN", None),
        "target_toggle_cycles": getattr(emulator, "TARGET_TOGGLE_CYCLES", None),
    }
    if solved and FLAG:
        result["flag"] = FLAG

    return jsonify(result)


if __name__ == "__main__":
    # WARNING: do NOT run with debug=True on a public server (it can leak environment variables and stack traces)
    app.run(host="0.0.0.0", port=5000, debug=False)
