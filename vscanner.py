from flask import Flask, render_template_string, request, jsonify
import nmap
import requests

app = Flask(__name__)

# Function to run the nmap scan
def scannn(target):
    print(f"Starting scan for {target}")
    scanner = nmap.PortScanner()

    # Run the scan on the given target IP
    scanner.scan(target, arguments='-p-')  # Use -p- to scan all ports

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

# Function to get the client IP address using an external API
def get_client_ip():
    try:
        # Use an external API to get the real public IP address
        response = requests.get('https://api.ipify.org?format=json')
        ip_data = response.json()
        return ip_data['ip']
    except requests.RequestException:
        # Fallback to Flask's remote_addr if the external request fails
        return request.remote_addr

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
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                flex-direction: column;
            }

            /* Page Layout */
            h1 {
                color: #0056b3;
                margin-bottom: 20px;
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

            /* Modern Button for Code Page */
            .code-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 15px 25px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: background-color 0.3s ease;
            }

            .code-button:hover {
                background-color: #218838;
            }

            /* Client IP Button */
            .ip-button {
                position: fixed;
                bottom: 80px;  /* Adjusted the gap to increase space between buttons */
                right: 20px;
                padding: 15px 25px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: background-color 0.3s ease;
            }

            .ip-button:hover {
                background-color: #0056b3;
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
                    if (data.results && Array.isArray(data.results)) {
                        // Display the scan results
                        let resultText = "Scan Results:\\n\\n";
                        data.results.forEach(line => {
                            resultText += line + "\\n";
                        });
                        document.getElementById("result").innerText = resultText;
                    } else {
                        document.getElementById("result").innerText = "Error: Invalid scan results.";
                    }
                })
                .catch(error => {
                    document.getElementById("result").innerText = "Error: " + error;
                });
            }

            function showClientIp() {
                // Make an AJAX request to the /get-client-ip endpoint
                fetch('/get-client-ip')
                .then(response => response.json())
                .then(data => {
                    if (data.ip) {
                        alert("Client IP: " + data.ip);
                    } else {
                        alert("Could not retrieve client IP.");
                    }
                })
                .catch(error => {
                    alert("Error: " + error);
                });
            }
        </script>
    </head>
    <body>
        <h1>Run Nmap Scan</h1>
        <input type="text" id="ip_address" placeholder="Enter IP Address" required>
        <button onclick="callFunction()">Run Scan</button>
        <pre id="result"></pre>
        
        <!-- Button to navigate to code page -->
        <a href="/code"><button class="code-button">View Source Code</button></a>

        <!-- Button to show client IP -->
        <button class="ip-button" onclick="showClientIp()">Show Client IP</button>
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
        
        # Return scan results
        return jsonify({"results": results})
    except Exception as e:
        print("Error during scanning:", str(e))
        return jsonify({"error": str(e)}), 500

# Route to get the client IP
@app.route("/get-client-ip", methods=["GET"])
def get_client_ip_route():
    ip = get_client_ip()
    return jsonify({"ip": ip})

# Route to show the source code
@app.route("/code")
def code_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Source Code</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 20px;
            }

            h1 {
                text-align: center;
                color: #0056b3;
            }

            pre {
                background-color: #fff;
                border: 1px solid #ccc;
                padding: 15px;
                font-family: "Courier New", Courier, monospace;
                font-size: 14px;
                color: #333;
                white-space: pre-wrap;
                word-wrap: break-word;
                max-width: 100%;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }

            button {
                background-color: #0056b3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
            }

            button:hover {
                background-color: #004494;
            }
        </style>
    </head>
    <body>
        <h1>Source Code</h1>
        <pre id="sourceCode">
from flask import Flask, render_template_string, request, jsonify
import nmap
import requests

app = Flask(__name__)

def scannn(target):
    # Nmap scanning logic here...
    pass

@app.route("/")
def index():
    # Main page HTML...
    pass

@app.route("/scan", methods=["POST"])
def scan():
    # Scan handling logic...
    pass

@app.route("/code")
def code_page():
    # Code page display...
    pass

if __name__ == "__main__":
    app.run(debug=True)
        </pre>
        <button onclick="copyCode()">Copy Code</button>

        <script>
            function copyCode() {
                const code = document.getElementById("sourceCode");
                const range = document.createRange();
                range.selectNode(code);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                document.execCommand("copy");
                alert("Code copied to clipboard!");
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)
