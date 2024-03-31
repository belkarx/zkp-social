import os

from openai import OpenAI

#can also use claude. in fact you should use claude. claude is great.
client = OpenAI()

from flask import Flask, redirect, render_template, request, url_for, make_response

app = Flask(__name__)

@app.route("/next", methods=["POST"])
def next():
    secret = request.form["secret"]
    if not request.cookies.get('secrets'):
        secrets = [secret]
    else:
        secrets = request.cookies.get('secrets').split("|||")
        secrets.append(secret)
    secrets = "|||".join(secrets)
    print(secrets)

    res = make_response(redirect(url_for("index")))
    res.set_cookie('secrets', secrets, max_age=60*60*24)
    return res

@app.route("/done", methods=["POST", "GET"])
def done():
    try:
        secrets = request.cookies.get('secrets').split("|||")
    except:
        return redirect(url_for("index"))
    print("DONE")
    print(secrets)
    if len(secrets) < 2:
        return redirect(url_for("index"))
    response = inference(generate_prompt(secrets))
    res = make_response(render_template("done.html", response=response))
    res.set_cookie('secrets', "", max_age=0)
    return res


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def inference(prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": prompt}], max_tokens=256)
    return response.choices[0].message.content

def generate_prompt(secrets):
    secrets_string = '\n'.join(secrets)
    return f"""You will see some claims below. Please state the overlap. If one person states things that are in contradiction, ignore what they've said. They may use first person - assume pronouns are referring to the testimonials before them.
    example:
    I am going to a party tomorrow
    he has plans tomorrow
    his parents are divorced and he's going to a party tomorrow to get over it
    response: "One of you is busy tomorrow" NOT "both of you are busy tomorrow", because it is one person in question when pronouns are used like that.
    Make sure to state the overlap, not the differences. If there is no overlap, state that. If there is overlap, state what it is. DO NOT state anything other than the overlap, this is very important.

    here are the claims:
{secrets_string}"""
