from flask import Flask, request, render_template_string
import socket
import threading
from queue import Queue

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Port Scanner Dashboard</title>
</head>
<body>
    <h1>Python Port Scanner</h1>
    <form method="post">
        Target IP or Domain:
        <input type="text" name="target">
        <button type="submit">Scan</button>
    </form>

    {% if results %}
        <h2>Scan Results</h2>
        <ul>
        {% for r in results %}
            <li>{{ r }}</li>
        {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
"""

def scan_ports(target):
    results = []
    queue = Queue()

    def scan_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)

            result = s.connect_ex((target, port))
            if result == 0:
                results.append(f"port {port} OPEN")

            s.close()
        except:
            pass
    def worker():
        while not queue.empty():
            port = queue.get()
            scan_port(port)
            queue.task_done()

    for port in range(1, 1025):
        queue.put(port)

    for _ in range(100):
        t = threading.Thread(target=worker)
        t.start()

    queue.join()
    return results

@app.route("/", methods=["GET", "POST"])
def home():
    results = []

    if request.method == "POST":
        target = request.form["target"]
        target = target.replace("http://", "").replae("https://", "").split("/")[0]
        results = scan_ports(target)

    return render_template_string(HTML, results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
