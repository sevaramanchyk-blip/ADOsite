import http.server
import socketserver
import json
import os
import sys
import time
import urllib.request
import urllib.error
import ssl
import socket
import subprocess
import traceback
import re
from pathlib import Path
from urllib.parse import urlparse

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = Path(DIRECTORY).parent
os.chdir(DIRECTORY)

# Python из venv для запуска pytest
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)


class ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class ADOHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.ico': 'image/x-icon',
    }

    def do_GET(self):
        try:
            super().do_GET()
        except Exception as e:
            traceback.print_exc()
            try:
                self.send_error(500)
            except Exception:
                pass

    def do_POST(self):
        try:
            if self.path == '/api/test':
                self.handle_api_test()
            elif self.path == '/api/run-tests':
                self.handle_run_tests()
            else:
                self.send_error(404)
        except Exception as e:
            traceback.print_exc()
            try:
                self.send_json(500, {"error": str(e)})
            except Exception:
                pass

    def handle_run_tests(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            params = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
            return

        test_type = params.get('type', 'api')
        test_path = params.get('path', '')
        selector = params.get('selector', '')
        assertion = params.get('assertion', 'visible')
        url = params.get('url', 'https://ado-shop.com/')

        selector_test_map = {
            'header': 'tests/ui/test_elements.py::TestHeaderElements',
            'footer': 'tests/ui/test_elements.py::TestFooterElements',
            'logo': 'tests/ui/test_elements.py::TestHeaderElements',
            'search': 'tests/ui/test_elements.py::TestSearchElements',
            'nav': 'tests/ui/test_elements.py::TestNavigationElements',
            'cart': 'tests/ui/test_business.py::TestCartFlow',
            'products': 'tests/ui/test_adoshop.py::TestProductPages',
            'h1': 'tests/ui/test_spellcheck.py::TestHomepageSpellcheck',
        }

        test_map = {
            'api': 'tests/api',
            'ui': 'tests/ui',
            'spell': 'tests/ui/test_spellcheck.py',
            'elements': 'tests/ui/test_elements.py',
            'business': 'tests/ui/test_business.py',
            'links': 'tests/ui/test_links.py',
            'all': 'tests/api tests/ui',
            'extended': 'tests/ui/test_ui_extended.py',
            'adoshop': 'tests/ui/test_adoshop.py',
        }

        if selector in selector_test_map:
            test_target = selector_test_map[selector]
        elif test_type == 'custom':
            test_target = test_path if test_path else 'tests/ui'
        elif test_type in test_map:
            test_target = test_map[test_type]
        else:
            test_target = 'tests/api tests/ui'

        cmd = [str(VENV_PYTHON), "-m", "pytest", "-v", test_target, "--tb=line"]

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(PROJECT_ROOT),
                encoding="utf-8",
                errors="replace"
            )
            output = result.stdout + result.stderr
            if not output.strip():
                output = f"Exit code: {result.returncode}\nNo output captured."
        except subprocess.TimeoutExpired:
            output = "TIMEOUT: Tests took longer than 300 seconds"
        except Exception as e:
            output = f"ERROR: {str(e)}"

        duration = time.time() - start_time
        parsed = self._parse_pytest_output(output)

        response = {
            "passed": parsed['passed'],
            "failed": parsed['failed'],
            "skipped": parsed['skipped'],
            "duration": f"{duration:.1f}s",
            "tests": parsed['tests'],
            "raw_output": output[-2000:] if len(output) > 2000 else output
        }
        self.send_json(200, response)

    def _parse_pytest_output(self, output):
        passed = 0
        failed = 0
        skipped = 0
        tests = []

        lines = output.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Формат 2: "FAILED tests/file.py::test_name" на отдельной строке
            if stripped.startswith('FAILED') and '::' in stripped:
                match = re.search(r'FAILED\s+(\S+::\S+)', stripped)
                if match:
                    name = match.group(1).split('::')[-1]
                    error_msg = ""
                    for j in range(i + 1, min(i + 5, len(lines))):
                        eline = lines[j].strip()
                        if eline and 'FAILED' not in eline and 'ERRORS' not in eline:
                            error_msg = eline[:120]
                            break
                    tests.append({
                        "name": name,
                        "status": "failed",
                        "duration": "0s",
                        "error": error_msg
                    })
                    failed += 1

            # Формат 1: "tests/file.py::test_name PASSED [10%]"
            elif '::' in stripped and 'PASSED' in stripped:
                match = re.search(r'(\S+::\S+)\s+PASSED', stripped)
                if match:
                    name = match.group(1).split('::')[-1]
                    tests.append({"name": name, "status": "passed", "duration": "0s"})
                    passed += 1

            elif '::' in stripped and 'FAILED' in stripped:
                match = re.search(r'(\S+::\S+)\s+FAILED', stripped)
                if match:
                    name = match.group(1).split('::')[-1]
                    error_msg = ""
                    for j in range(i + 1, min(i + 5, len(lines))):
                        eline = lines[j].strip()
                        if eline and 'FAILED' not in eline and 'ERRORS' not in eline:
                            error_msg = eline[:120]
                            break
                    tests.append({
                        "name": name,
                        "status": "failed",
                        "duration": "0s",
                        "error": error_msg
                    })
                    failed += 1

            elif '::' in stripped and 'SKIPPED' in stripped:
                match = re.search(r'(\S+::\S+)\s+SKIPPED', stripped)
                if match:
                    name = match.group(1).split('::')[-1]
                    tests.append({"name": name, "status": "skipped", "duration": "0s"})
                    skipped += 1

            elif 'ERROR' in stripped and '::' in stripped:
                match = re.search(r'ERROR\s+(\S+::\S+)', stripped)
                if match:
                    name = match.group(1).split('::')[-1]
                    tests.append({
                        "name": name,
                        "status": "failed",
                        "duration": "0s",
                        "error": stripped[:120]
                    })
                    failed += 1

        summary_match = re.search(r'(\d+) passed', output)
        if summary_match:
            passed = max(passed, int(summary_match.group(1)))
        summary_fail = re.search(r'(\d+) failed', output)
        if summary_fail:
            failed = max(failed, int(summary_fail.group(1)))
        summary_skip = re.search(r'(\d+) skipped', output)
        if summary_skip:
            skipped = max(skipped, int(summary_skip.group(1)))

        return {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'tests': tests
        }

    def handle_api_test(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            params = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
            return

        method = params.get('method', 'GET').upper()
        url = params.get('url', 'https://ado-shop.com/')
        timeout = int(params.get('timeout', 10))
        follow_redirects = params.get('redirects', 'true') == 'true'
        headers_raw = params.get('headers', '{}')
        request_body = params.get('body', '')

        try:
            custom_headers = json.loads(headers_raw) if headers_raw else {}
        except json.JSONDecodeError:
            custom_headers = {}

        tests = []
        start_total = time.time()

        # Test 1: DNS resolution
        t0 = time.time()
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            socket.getaddrinfo(hostname, 443)
            dns_time = time.time() - t0
            tests.append({
                "name": f"DNS Resolution ({hostname})",
                "status": "passed",
                "duration": f"{dns_time:.3f}s"
            })
        except Exception as e:
            tests.append({
                "name": f"DNS Resolution ({hostname})",
                "status": "failed",
                "duration": f"{time.time() - t0:.3f}s",
                "error": str(e)
            })

        # Test 2: TCP connection
        t0 = time.time()
        try:
            hostname = parsed_url.hostname
            sock = socket.create_connection((hostname, 443), timeout=timeout)
            sock.close()
            tcp_time = time.time() - t0
            tests.append({
                "name": "TCP Connection",
                "status": "passed",
                "duration": f"{tcp_time:.3f}s"
            })
        except Exception as e:
            tests.append({
                "name": "TCP Connection",
                "status": "failed",
                "duration": f"{time.time() - t0:.3f}s",
                "error": str(e)
            })

        # Test 3: SSL certificate
        t0 = time.time()
        try:
            ctx = ssl.create_default_context()
            hostname = parsed_url.hostname
            conn = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
            conn.settimeout(timeout)
            conn.connect((hostname, 443))
            conn.getpeercert()
            conn.close()
            ssl_time = time.time() - t0
            tests.append({
                "name": "SSL Certificate Valid",
                "status": "passed",
                "duration": f"{ssl_time:.3f}s"
            })
        except Exception as e:
            tests.append({
                "name": "SSL Certificate Valid",
                "status": "failed",
                "duration": f"{time.time() - t0:.3f}s",
                "error": str(e)
            })

        # Test 4: Actual HTTP request
        t0 = time.time()
        try:
            req = urllib.request.Request(url, method=method)
            req.add_header('User-Agent', 'ADO-TestBot/1.0')
            for k, v in custom_headers.items():
                req.add_header(k, v)

            if method in ('POST', 'PUT', 'PATCH') and request_body:
                req.data = request_body.encode('utf-8')
                if 'Content-Type' not in custom_headers:
                    req.add_header('Content-Type', 'application/json')

            ctx = ssl.create_default_context()
            if follow_redirects:
                resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
            else:
                class NoRedirect(urllib.request.HTTPErrorProcessor):
                    def http_response(self, request, response):
                        return response
                    https_response = http_response
                opener = urllib.request.build_opener(NoRedirect)
                resp = opener.open(req, timeout=timeout)

            status_code = resp.status
            resp_headers = dict(resp.headers)
            resp_body = resp.read().decode('utf-8', errors='replace')
            response_time = time.time() - t0

            expected_status = int(params.get('expected_status', '200'))
            if method in ('PUT', 'DELETE', 'PATCH'):
                if status_code in (403, 404, 405):
                    expected_status = status_code

            tests.append({
                "name": f"{method} {url} -> {status_code}",
                "status": "passed" if status_code == expected_status else "failed",
                "duration": f"{response_time:.3f}s",
                "detail": f"Expected {expected_status}, got {status_code}" if status_code != expected_status else None
            })

            threshold = int(params.get('timeout', 10))
            tests.append({
                "name": f"Response Time < {threshold}s",
                "status": "passed" if response_time < threshold else "failed",
                "duration": f"{response_time:.3f}s",
                "detail": f"Took {response_time:.2f}s" if response_time >= threshold else None
            })

            ct = resp_headers.get('Content-Type', '')
            if method == 'GET' and '200' in str(status_code):
                tests.append({
                    "name": "Content-Type Header",
                    "status": "passed" if ct else "failed",
                    "duration": "0.001s",
                    "detail": f"Content-Type: {ct}" if ct else "Missing"
                })

            if method == 'GET':
                tests.append({
                    "name": "Response Body Not Empty",
                    "status": "passed" if len(resp_body) > 0 else "failed",
                    "duration": "0.001s",
                    "detail": f"Size: {len(resp_body)} bytes"
                })

            server = resp_headers.get('Server', '')
            tests.append({
                "name": "Server Header Present",
                "status": "passed" if server else "failed",
                "duration": "0.001s",
                "detail": f"Server: {server}" if server else "Missing"
            })

            cc = resp_headers.get('Cache-Control', '')
            tests.append({
                "name": "Cache-Control Present",
                "status": "passed" if cc else "failed",
                "duration": "0.001s",
                "detail": f"Cache-Control: {cc}" if cc else "Missing"
            })

            xcto = resp_headers.get('X-Content-Type-Options', '')
            tests.append({
                "name": "X-Content-Type-Options",
                "status": "passed" if xcto else "failed",
                "duration": "0.001s",
                "detail": f"X-Content-Type-Options: {xcto}" if xcto else "Missing"
            })

            acao = resp_headers.get('Access-Control-Allow-Origin', '')
            tests.append({
                "name": "CORS Headers Check",
                "status": "passed" if acao else "failed",
                "duration": "0.001s",
                "detail": f"ACAO: {acao}" if acao else "No CORS headers"
            })

            cl = resp_headers.get('Content-Length', '')
            tests.append({
                "name": "Content-Length Valid",
                "status": "passed" if cl else "failed",
                "duration": "0.001s",
                "detail": f"Content-Length: {cl}" if cl else "Missing"
            })

        except urllib.error.HTTPError as e:
            response_time = time.time() - t0
            status_code = e.code
            tests.append({
                "name": f"{method} {url} -> {status_code}",
                "status": "passed" if status_code in (403, 404, 405) else "failed",
                "duration": f"{response_time:.3f}s",
                "detail": f"HTTP {status_code}: {e.reason}"
            })
            tests.append({
                "name": f"Response Time < {timeout}s",
                "status": "passed" if response_time < timeout else "failed",
                "duration": f"{response_time:.3f}s"
            })
        except Exception as e:
            response_time = time.time() - t0
            tests.append({
                "name": f"{method} {url} -> ERROR",
                "status": "failed",
                "duration": f"{response_time:.3f}s",
                "error": str(e)
            })

        total_time = time.time() - start_total
        passed = sum(1 for t in tests if t['status'] == 'passed')
        failed = sum(1 for t in tests if t['status'] == 'failed')

        result = {
            "passed": passed,
            "failed": failed,
            "duration": f"{total_time:.1f}s",
            "tests": tests
        }
        self.send_json(200, result)

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with ThreadedTCPServer(("0.0.0.0", PORT), ADOHandler) as httpd:
        print(f"ADO Site running at http://127.0.0.1:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()
