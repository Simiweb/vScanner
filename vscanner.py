from flask import Flask, render_template_string, request, jsonify
import nmap

app = Flask(__name__)


# Function to run the nmap scan
def scannn(target):
    print(f"Starting scan for {target}")
    scanner = nmap.PortScanner()

    # Run the scan on the given target IP
    scanner.scan(target)

    results = []
    for host in scanner.all_hosts():
        results.append(f"Host: {host}")
        results.append(f"State: {scanner[host].state()}")
        for proto in scanner[host].all_protocols():
            results.append(f"Protocol: {proto}")
            ports = scanner[host][proto].keys()
            for port in ports:
                results.append(
                    f"Port: {port} State: {scanner[host][proto][port]['state']}"
                )
    print("Scan Results:", results)
    return results


# Define the main route for the website
@app.route("/")
def index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nmap Scanner</title>
        <style>
            /* General Reset */
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                line-height: 1.6;
            }

            /* Page Layout */
            h1 {
                text-align: center;
                margin-top: 20px;
                color: #0056b3;
            }

            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }

            /* Input Field and Button */
            input[type="text"] {
                width: 300px;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
            }

            button {
                padding: 10px 20px;
                background-color: #0056b3;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover {
                background-color: #004494;
            }

            /* Result Section */
            pre#result {
                width: 90%;
                max-width: 600px;
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-family: "Courier New", Courier, monospace;
                font-size: 14px;
                color: #222;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
        </style>
        <script>
            function callFunction() {
                // Get the IP address from the input field
                const ip = document.getElementById('ip_address').value;

                // Show a loading message
                document.getElementById("result").innerText = "Processing...";

                // Make an AJAX request to the /scan endpoint
                fetch('/scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ ip_address: ip })
                })
                .then(response => response.json())
                .then(data => {
                    // Display the scan results
                    let resultText = "Scan Results:\\n\\n";
                    data.results.forEach(line => {
                        resultText += line + "\\n";
                    });
                    document.getElementById("result").innerText = resultText;
                })
                .catch(error => {
                    document.getElementById("result").innerText = "Error: " + error;
                });
            }
        </script>
    </head>
    <body>
        <h1>Run Nmap Scan</h1>
        <input type="text" id="ip_address" placeholder="Enter IP Address" required>
        <button onclick="callFunction()">Run Scan</button>
        <pre id="result"></pre>
    </body>
    </html>
    """
    return render_template_string(html_content)


# Route to handle the scan
@app.route("/scan", methods=["POST"])
def scan():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging output
        target = data["ip_address"]
        results = scannn(target)
        return jsonify({"results": results})
    except Exception as e:
        print("Error during scanning:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
