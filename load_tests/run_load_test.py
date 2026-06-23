import subprocess
import csv
import sys
from pathlib import Path


def run_load_test(
    users=10, spawn_rate=5, run_time="30s"
) -> dict:
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "load_test_stats.csv"

    if csv_path.exists():
        csv_path.unlink()

    cmd = [
        sys.executable, "-m", "locust",
        "-f", "locustfile.py",
        "--host", "https://ado-shop.com",
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--run-time", run_time,
        "--csv", str(results_dir / "load_test"),
        "--only-summary",
        "--skip-log-setup",
    ]

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=120, cwd=str(Path(__file__).parent)
        )
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired:
        return {"error": "Тест превысил лимит времени (120 сек)"}

    stats_path = results_dir / "load_test_stats.csv"
    if not stats_path.exists():
        return {
            "error": "Файл результатов не найден",
            "stdout": stdout[-2000:] if stdout else "",
            "stderr": stderr[-1000:] if stderr else "",
        }

    return parse_results(stats_path, stdout)


def parse_results(csv_path: Path, raw_output: str) -> dict:
    if not csv_path.exists():
        return {"error": "Файл результатов не найден"}

    stats = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats.append(row)

    if not stats:
        return {"error": "Нет данных в csv"}

    total_requests = 0
    total_failures = 0
    avg_response = 0
    max_response = 0
    min_response = float("inf")
    rps = 0
    endpoints = []

    for row in stats:
        name = row.get("Name", "")
        if name == "Aggregated":
            total_requests = int(row.get("Request Count", 0))
            total_failures = int(row.get("Failure Count", 0))
            avg_response = float(
                row.get("Average Response Time", 0) or 0
            )
            max_response = float(
                row.get("Max Response Time", 0) or 0
            )
            min_response = float(
                row.get("Min Response Time", 0) or 0
            )
            rps = float(row.get("Requests/s", 0) or 0)
        elif name:
            endpoints.append({
                "name": name,
                "requests": row.get("Request Count", "0"),
                "failures": row.get("Failure Count", "0"),
                "avg_ms": row.get(
                    "Average Response Time", "0"
                ),
                "rps": row.get("Requests/s", "0"),
            })

    success_rate = (
        ((total_requests - total_failures) / total_requests * 100)
        if total_requests > 0 else 0
    )

    if success_rate >= 95:
        emoji = "🟢"
    elif success_rate >= 70:
        emoji = "🟡"
    else:
        emoji = "🔴"

    table = f"<b>{emoji} Нагрузочный тест</b>\n\n"

    table += "<b>📊 Общая статистика</b>\n"
    table += "<code>┌─────────────────┬──────────┐\n"
    table += "│ Параметр        │ Значение │\n"
    table += "├─────────────────┼──────────┤\n"
    table += f"│ Всего запросов  │ {total_requests:>8} │\n"
    table += f"│ Успешных        │ {total_requests - total_failures:>8} │\n"
    table += f"│ Ошибок          │ {total_failures:>8} │\n"
    table += f"│ Успешность      │ {success_rate:>7.1f}% │\n"
    table += f"│ RPS             │ {rps:>8.1f} │\n"
    table += "└─────────────────┴──────────┘</code>\n\n"

    table += "<b>⏱ Время отклика (мс)</b>\n"
    table += "<code>┌─────────────────┬──────────┐\n"
    table += "│ Параметр        │ Значение │\n"
    table += "├─────────────────┼──────────┤\n"
    table += f"│ Минимальное     │ {min_response:>8.0f} │\n"
    table += f"│ Среднее         │ {avg_response:>8.0f} │\n"
    table += f"│ Максимальное    │ {max_response:>8.0f} │\n"
    table += "└─────────────────┴──────────┘</code>\n\n"

    if endpoints:
        table += "<b>📄 По эндпоинтам</b>\n"
        table += "<code>┌─────────────────────────────────────┬──────┬─────────┐\n"
        table += "│ Эндпоинт                          │ Запр │ Среднее │\n"
        table += "├─────────────────────────────────────┼──────┼─────────┤\n"
        for ep in endpoints:
            name = ep['name']
            if len(name) > 35:
                name = name[:32] + "..."
            table += f"│ {name:<35} │ {ep['requests']:>4} │ {float(ep['avg_ms']):>6.0f}ms │\n"
        table += "└─────────────────────────────────────┴──────┴─────────┘</code>"

    return {"text": table}


if __name__ == "__main__":
    result = run_load_test()
    if "error" in result:
        print(f"ОШИБКА: {result['error']}")
    else:
        print(result["text"])
