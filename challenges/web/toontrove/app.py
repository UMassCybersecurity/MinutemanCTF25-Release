from flask import Flask, render_template, redirect, request, session, send_file
from flask_session import Session
from urllib.request import urlretrieve
import os
#import shutil
from uuid import uuid4
import random
import string
import sys

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
os.makedirs(f"uploads", exist_ok=True)

@app.route('/')
def root():
    if not session or not session['uuid']:
        session["uuid"] = uuid4()
        session["counter"] = 0
        os.makedirs(f"uploads/{session['uuid']}", exist_ok=True)
        #shutil.copytree(f"starter_images", f"uploads/{session['uuid']}", dirs_exist_ok=True)
    images = os.listdir(f"uploads/{session['uuid']}")
    return render_template('index.html', images=images)

@app.get('/images/<image>')
def get_image(image):
    if not session or not session['uuid']:
        return redirect("/")
    return send_file(f"uploads/{session['uuid']}/{image}")

@app.post('/upload')
def upload():
  if not session or not session['uuid']:
    return redirect("/")

  try:
    url = request.form['url']
    local_loc, headers = urlretrieve(url)
    file_type = headers["Content-Type"].split("/")[1]

    image_name = f"image-{session['counter']}.{file_type}"
    session["counter"] += 1

    upload_loc = f"uploads/{session['uuid']}/{image_name}"
    urlretrieve(url, upload_loc)
    return redirect("/")
  except Exception as e:
    return "Please make sure the url you entered is a valid image url.", 500
  
@app.route("/clear_session")
def logout():
    session['uuid'] = None
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
