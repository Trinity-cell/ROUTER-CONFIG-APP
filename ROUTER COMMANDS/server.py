from flask import request, render_template, Flask, session, url_for, Response
from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = "sessionsecretkey"

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
       session['hostname'] = request.form.get("hostname")
       session["interfaces"] = int(request.form.get("interface_no"))
       session["current"] = 0
       session["interface_ips"] = []
       session["interface_names"] = []
       return(redirect(url_for("interfaces")))

    return render_template("index.html")

@app.route("/interfaces", methods=['GET', 'POST'])
def interfaces():
    if request.method == "POST":
        session["interface_names"].append(request.form.get("interface_name"))
        session["interface_ips"].append(request.form.get("interface_ip"))
        session["current"] += 1

        if session["current"] >= session["interfaces"]:
            return redirect(url_for("results"))
        else:
            return redirect(url_for("interfaces"))
    return render_template("interfaces.html",current=session["current"] + 1,
        total=session["interfaces"])

@app.route("/results", methods=["GET"])
def results():
    hostname = session["hostname"]
    interfaces = session["interface_names"]
    ips = session["interface_ips"]

    commands = []
    commands.append("no")
    commands.append("enable")
    commands.append("configure terminal")
    commands.append(f"hostname {hostname}")

    for i in range(len(interfaces)):
        commands.append(f"interface {interfaces[i]}")
        commands.append(f"ip address {ips[i]}")
        commands.append("no shutdown")
    commands.append("exit")

    return render_template("result.html", commands=commands)

@app.route("/download")
def download():
    hostname = session["hostname"]
    interfaces = session["interface_names"]
    ips = session["interface_ips"]

    lines = []
    lines.append("no")
    lines.append("enable")
    lines.append("configure terminal")
    lines.append(f"hostname {hostname}")

    for i in range(len(interfaces)):
        lines.append(f"interface {interfaces[i]}")
        lines.append(f"ip address {ips[i]}")
        lines.append("no shutdown")
    lines.append("exit")
    output = "\n".join(lines)

    return Response(
        output,
        mimetype="text/plain",
        headers={
            "Content-Disposition":f"attachment;filename={hostname}_config.txt"
        }
    )

if __name__ == "__main__":

    app.run(debug=True)

