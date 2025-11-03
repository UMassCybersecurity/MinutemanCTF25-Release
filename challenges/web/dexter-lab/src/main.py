from flask import Flask, request, send_file, abort
import os
import urllib.parse
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "files/vault"))

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<style>
            body { font-family: 'Inter', sans-serif; background-color: #3a3120; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #72c8d5; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(57, 255, 20, 0.1); }
            h1 { color: #FE4902; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }
            h3 { color: #FE4902; margin-top: 15px; }
            a { color: #FE4902; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul { list-style-type: none; padding-left: 0; }
            li { background-color: white; margin-bottom: 8px; padding: 10px; border-radius: 6px; }
        </style>
        <div class="container">
            <h1>Dexter's Laboratory</h1>
            <p></p>
            
            <h3>Available Files in the Vault</h3>
            <ul>
                <!-- Updated link: simple filename works for safe files -->
                <li><a href="/read?file=inner-thoughts.txt">inner-thoughts</a></li>
                <li><a href="/read?file=on-this-day.txt">twas-the-day</a> </li>
            </ul>
        </div>
    '''

@app.route('/read')
def read():

    raw_qs = request.environ.get('QUERY_STRING', '')
    raw_file = ''
    for q in raw_qs.split('&'):
        if q.startswith('file='):
            raw_file = q.split('=', 1)[1]
            break

    if not raw_file:
        return "Error: Missing 'file' parameter", 400

    is_traversal_attempt = '..' in raw_file
    if is_traversal_attempt and '%' not in raw_file:
        return "I see you're trying to break the vault. Not Allowed!!", 400

    filename = urllib.parse.unquote(raw_file)

    joined_path = os.path.join(BASE_DIR, filename)
    filepath = os.path.abspath(joined_path)

    if not os.path.isfile(filepath):
        print(f"Attempted access to non-existent file: {filepath}", file=sys.stderr)
        abort(404)

    try:
        print(f"Successfully serving file: {filepath}", file=sys.stderr)
        return send_file(filepath)
    except PermissionError:
        abort(403)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        abort(500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
