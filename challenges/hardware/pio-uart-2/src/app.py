# app.py
import os
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

# Assemble PIO
from adafruit_pioasm import assemble

# Your emulator module (must define UART_PIN, UART_CYCLE_RATE, UART_WAIT_TIME and run_emulator)
import emulator

# Optional: read flag from environment
FLAG = os.environ.get("FLAG")

# Files / sizes
ALLOWED_EXTENSIONS = {"asm", "txt", "pio"}
MAX_FILE_SIZE = 32 * 1024  # 32 KiB
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-this")
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024  # global maximum request size

emulator_variables = {
    "uart_pin": emulator.UART_RX_PIN,
    "rts_pin": emulator.UART_RTS_PIN,
    "uart_cycle_rate": emulator.UART_CYCLE_RATE,
    "rts_active_range": emulator.UART_RTS_ACTIVE_RANGE,
    "rts_inactive_range": emulator.UART_RTS_INACTIVE_RANGE,
    "uart_valid_bytes_count": emulator.UART_VALID_BYTES_COUNT
}

def allowed_filename(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    # show challenge parameters to user
    return render_template(
        "index.html",
        **emulator_variables,
        flag=None,
    )


@app.route("/submit", methods=["POST"])
def submit():
    """
    Handle form POST: assemble, run emulator, show logs and flag if solved.
    """
    source = None

    # 1) read source from textarea if present
    if "source" in request.form and request.form["source"].strip():
        source = request.form["source"].strip()
    # 2) else read uploaded file
    elif "file" in request.files:
        f = request.files["file"]
        if f and f.filename:
            filename = secure_filename(f.filename)
            if not allowed_filename(filename):
                flash("Invalid file type. Allowed: .asm, .txt", "danger")
                return redirect(url_for("index"))

            # size check (simple)
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
            if size > MAX_FILE_SIZE:
                flash(f"Uploaded file too large ({size} bytes). Limit: {MAX_FILE_SIZE} bytes.", "danger")
                return redirect(url_for("index"))

            try:
                source = f.read().decode("utf-8", errors="replace")
            except Exception as e:
                flash(f"Failed to read uploaded file: {e}", "danger")
                return redirect(url_for("index"))

    if not source:
        flash("No PIO source provided. Paste in the box or upload a file.", "danger")
        return redirect(url_for("index"))

    # 3) assemble
    try:
        opcodes_iter = assemble(source)
    except Exception as e:
        app.logger.debug("Assemble traceback:\n%s", traceback.format_exc())
        flash(f"Assembly failed: {e}", "danger")
        return render_template(
            "index.html",
            assembly_error=str(e),
            source=source,
            **emulator_variables,
            flag=None,
        )

    # convert to list[int]
    try:
        opcodes = list(opcodes_iter)
    except Exception as e:
        app.logger.debug("Opcode conversion error:\n%s", traceback.format_exc())
        flash(f"Failed to process assembled opcodes: {e}", "danger")
        return render_template(
            "index.html",
            execution_error=str(e),
            source=source,
            **emulator_variables,
            flag=None,
        )

    # 4) run emulator. We intentionally don't pass max_cycles here and let emulator use its default;
    # if you want to expose max_cycles as a form field, we can add it later.
    try:
        solved, logs = emulator.run_emulator(opcodes)
    except TypeError:
        # maybe emulator expects list[int], max_cycles optional
        try:
            solved, logs = emulator.run_emulator(list(opcodes))
        except Exception as e:
            app.logger.error("Emulator raised while running (second attempt):\n%s", traceback.format_exc())
            flash(f"Emulator execution failed: {e}", "danger")
            return render_template(
                "index.html",
                execution_error=str(e),
                source=source,
                **emulator_variables,
                flag=None,
            )
    except Exception as e:
        app.logger.error("Emulator raised while running:\n%s", traceback.format_exc())
        flash(f"Emulator execution failed: {e}", "danger")
        return render_template(
            "index.html",
            execution_error=str(e),
            source=source,
            **emulator_variables,
            flag=None,
        )

    # 5) result handling: show logs and flag only on success
    revealed_flag = None
    if solved:
        if FLAG:
            revealed_flag = FLAG
            flash("✅ Success! Flag revealed below.", "success")
        else:
            flash("✅ Success! (FLAG not set on server.)", "success")
    else:
        flash("❌ Incorrect — your program did not meet the emulator's checks.", "warning")

    return render_template(
        "index.html",
        source=source,
        assembled=opcodes,
        logs=logs,
        **emulator_variables,
        flag=revealed_flag,
    )


@app.route("/api/submit", methods=["POST"])
def api_submit():
    """
    JSON API:
      POST { "source": "<asm>", optional "max_cycles": int }
    Returns:
      { ok: bool, solved: bool, logs: str, maybe flag }
    """
    data = request.get_json(force=True, silent=True)
    if not data or "source" not in data:
        return jsonify({"ok": False, "error": "Missing 'source' in JSON body"}), 400

    source = data["source"]
    if not isinstance(source, str) or not source.strip():
        return jsonify({"ok": False, "error": "Invalid or empty 'source'"}), 400

    # optional max_cycles
    max_cycles = data.get("max_cycles", None)

    # assemble
    try:
        opcodes_iter = assemble(source)
        opcodes = list(opcodes_iter)
    except Exception as e:
        app.logger.debug("Assemble exception: %s", traceback.format_exc())
        return jsonify({"ok": False, "stage": "assemble", "error": str(e)}), 400

    # run emulator (try to pass max_cycles if provided)
    try:
        if isinstance(max_cycles, int):
            solved, logs = emulator.run_emulator(opcodes, max_cycles)
        else:
            solved, logs = emulator.run_emulator(opcodes)
    except Exception as e:
        app.logger.error("Emulator exception: %s", traceback.format_exc())
        return jsonify({"ok": False, "stage": "execute", "error": str(e)}), 500

    result = {"ok": True, "solved": bool(solved), "logs": logs}
    if solved and FLAG:
        result["flag"] = FLAG

    return jsonify(result)


if __name__ == "__main__":
    # WARNING: do not enable debug=True on a public server (it can leak env vars)
    app.run(host="0.0.0.0", port=5000, debug=False)
