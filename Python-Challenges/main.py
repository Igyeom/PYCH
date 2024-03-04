from flask import *
from PIL import Image, ImageDraw, ImageFont
from time import sleep
import io
import requests
import os
import sys
import json
import secrets
from datetime import datetime
from random import randint
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
sessions = {}
verification_codes = {}

'''
Certificate Generation Code proudly stolen from GeeksForGeeks ;-)
'''

def coupons(names: list, certificate: str, font_path: str):
      
  for name in names:
        
    # adjust the position according to 
    # your sample
    text_y_position = 800 
      
    # opens the image
    img = Image.open(certificate, mode ='r')
        
    # gets the image width
    image_width = img.width
        
    # gets the image height
    image_height = img.height 
      
    # creates a drawing canvas overlay 
    # on top of the image
    draw = ImageDraw.Draw(img)
      
    # gets the font object from the 
    # font file (TTF)
    font = ImageFont.truetype(
      font_path,
      200 # change this according to your needs
    )
      
    # fetches the text width for 
    # calculations later on
    text_width, _ = draw.textsize(name, font = font)
      
    draw.text(
      (
        # this calculation is done 
        # to centre the image
        (image_width - text_width) / 2,
        text_y_position
      ),
      name,
      font = font        )
      
    # saves the image in png format
    img.save("{}.png".format(name))

@app.errorhandler(404)
def not_found(error):
  return Markup("<script>location.href = history.back();</script>")

@app.route('/link-github')
def link_github():
  with open("static/users.json", "r+") as f:
    content = f.read().replace(request.args["email"], request.args["username"])
    f.seek(0)
    f.truncate(0)
    f.write(content)
  with open("static/submissions.json", "r+") as f:
    content = f.read().replace(request.args["email"], request.args["username"])
    f.seek(0)
    f.truncate(0)
    f.write(content)
  return render_template("success.html")

@app.route('/github-auth')
def github_auth():
  return render_template("github-auth.html", email=request.args["email"])
    

@app.route('/verify')
def verify():
  global verification_codes
  smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  smtp_server.login("pythonchallengesgis", os.getenv("APP_PASSWORD"))
  verification_codes[request.args["email"]] = str(randint(100000, 999999))
  smtp_server.sendmail("pythonchallengesgis@gmail.com", request.args["email"], "Your verification code is " + verification_codes[request.args["email"]] + ". Do not share this code with anyone. (If this email was not meant to be received, ignore and immediately delete this email.)")
  smtp_server.quit()
  return redirect("link?email=" + request.args["email"])

@app.route('/verify@<code>')
def verify_code(code):
  if code == verification_codes[request.args["email"]]:
    return redirect("github-auth?email=" + request.args["email"])

@app.route('/link')
def link():
  return render_template("link.html")


@app.route('/@<path:name>')
def profile(name):
  with open('static/users.json', 'r+') as f:
    users = json.load(f)
    for i in users:
      if i["user"] == name:
        return render_template("profile.html", name=i["user"], avatar=i["avatar"], points=i["points"], joined=i["joined"], rank=sorted(users, key=lambda d: d["points"])[::-1].index(i)+1)
  return Markup("<script>location.href = history.back();</script>")

@app.route('/me')
def me():
  if "SESSION" in request.cookies:
    try:
      return redirect("@" + list(sessions.keys())[list(sessions.values()).index(request.cookies.get("SESSION"))])
    except ValueError:
      return redirect("..")
  else:
    return redirect("..")

@app.route('/live')
def live():
  with open("./static/challenges.tsv", "r") as f:
      return render_template("live.html", sheet=f.read(), button=Markup('<div onclick="location.href = \'logout\'"; style="height: 40pt; width: 200px; margin: auto; background: orange; color: black; font-size: 30pt; cursor: pointer;">Log Out</div><br><div onclick="location.href = \'me\'"; style="height: 40pt; width: 200px; margin: auto; background: limegreen; color: black; font-size: 30pt; cursor: pointer;">Profile</div><br><div onclick="location.href = \'claim\'"; style="height: 40pt; width: 450px; margin: auto; background: coral; color: black; font-size: 30pt; cursor: pointer;">Claim Certificate</div><br><div onclick="location.href = \'rank\';" style="height: 40pt; width: 450px; margin: auto; background: black; color: white; font-size: 30pt; cursor: pointer;">Global Leaderboard</div>' if "SESSION" in request.cookies else '<div onclick="login();" style="height: 40pt; width: 450px; margin: auto; background: white; color: black; font-size: 30pt; cursor: pointer;">Login with GitHub</div><br><div onclick="location.href = \'rank\';" style="height: 40pt; width: 500px; margin: auto; background: black; color: white; font-size: 30pt; cursor: pointer;">Global Leaderboard</div>'))

@app.route('/')
def home():
  with open("./static/challenges.tsv", "r") as f:
    return render_template("home.html", sheet=f.read(), button=Markup('<div onclick="location.href = \'logout\'"; style="height: 40pt; width: 200px; margin: auto; background: orange; color: black; font-size: 30pt; cursor: pointer;">Log Out</div><br><div onclick="location.href = \'me\'"; style="height: 40pt; width: 200px; margin: auto; background: limegreen; color: black; font-size: 30pt; cursor: pointer;">Profile</div><br><div onclick="location.href = \'claim\'"; style="height: 40pt; width: 450px; margin: auto; background: coral; color: black; font-size: 30pt; cursor: pointer;">Claim Certificate</div><br><div onclick="location.href = \'rank\';" style="height: 40pt; width: 450px; margin: auto; background: black; color: white; font-size: 30pt; cursor: pointer;">Global Leaderboard</div>' if "SESSION" in request.cookies else '<div onclick="login();" style="height: 40pt; width: 450px; margin: auto; background: white; color: black; font-size: 30pt; cursor: pointer;">Login with GitHub</div><br><div onclick="location.href = \'rank\';" style="height: 40pt; width: 500px; margin: auto; background: black; color: white; font-size: 30pt; cursor: pointer;">Global Leaderboard</div>'))

@app.route('/claim')
def claim():
  if "SESSION" in request.cookies:
    try:
      name = list(sessions.keys())[list(sessions.values()).index(request.cookies.get("SESSION"))]
    except ValueError:
      return redirect("..")
  else:
    return redirect("..")

  with open('static/users.json', 'r+') as f:
    users = json.load(f)
    for i in users:
      if i["user"] == name:
        if i["points"] >= 3000:
          template = "GamesMasters"
        elif i["points"] >= 2000:
          template = "Diamond"
        elif i["points"] >= 1000:
          template = "Ruby"
        elif i["points"] >= 500:
          template = "Gold"
        elif i["points"] >= 250:
          template = "Silver"
        elif i["points"] >= 100:
          template = "Bronze"
        else:
          return redirect("..")
    
  # path to font
  FONT = "font.ttf"
      
  # path to sample certificate
  
  CERTIFICATE = template + ".png"
      
  coupons([name], CERTIFICATE, FONT)
  sleep(2)
  data = io.BytesIO()

  with open(name+".png", "rb") as f:
    data.write(f.read())

  data.seek(0)

  os.remove(name+".png")
  
  return send_file(data, mimetype='image/png')

@app.route('/submit')
def submit():
  return render_template('submit.html')

@app.route('/submit-process', methods=["POST"])
def submit_process():
  with open('static/submissions.json', 'r+') as f:
    submissions = json.load(f)
    if "SESSION" in request.cookies:
      try:
        submissions.append({"user": list(sessions.keys())[list(sessions.values()).index(request.cookies.get("SESSION"))], "approved": True, "challenge": request.form['code'], "link": request.form['link']})
        f.seek(0)
        f.truncate(0)
        json.dump(submissions, f, indent=4)
        return render_template("success.html")
      except ValueError:
        return redirect("..")
    else:
      return redirect("..")

@app.route('/rank')
def rank():
  with open('static/users.json', 'r+') as f:
    users = json.load(f)
    for i in users:
      return render_template("leaderboard.html", points=", ".join([str(i["points"]) for i in sorted(users, key=lambda d: d["points"])[::-1]]), names=", ".join([i["user"] for i in sorted(users, key=lambda d: d["points"])[::-1]]))
  
@app.route('/logout')
def logout():
  global sessions
  sessions = {key:val for key, val in sessions.items() if val != request.cookies.get("SESSION")}
  
  resp = make_response(redirect(".."))
  resp.set_cookie("SESSION", "ou", max_age=0)

  return resp

@app.route('/login')
def login():
  try:
    data = json.loads(requests.get("https://api.github.com/user", headers={"Authorization": "Bearer " + requests.post("https://github.com/login/oauth/access_token", {"client_id": "a1e884efc8b5b30c4cc3", "client_secret": os.getenv("SECRET"), "code": request.args["code"], "redirect_uri": "http://python-challenges.igyeom2.repl.co/login"}).text[13:-36]}).text)
    new_user = True
    with open('static/users.json', 'r+') as f:
      users = json.load(f)
      for i in users:
        if i["user"] == data["login"]:
          new_user = False
      if new_user:
        users.insert(0, {"user": data["login"], "school": None, "birth": None, "certified": [], "points": 0, "joined": str(datetime.now()), "avatar": data["avatar_url"]})
        
        f.seek(0)
        f.truncate(0)
        json.dump(users, f, indent=4)

    resp = make_response(redirect(".."))
    
    session = secrets.token_urlsafe(24)
    sessions.update({data["login"]: session})
    
    resp.set_cookie("SESSION", session)
    
    return resp
  except:
    return "ERROR"

app.run(host='0.0.0.0', port=8080)
