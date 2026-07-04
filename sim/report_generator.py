from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAST = ROOT / "last_run.txt"
OUT = ROOT / "report.html"


def main():
    if not LAST.exists():
        print("last_run.txt not found")
        return

    txt = LAST.read_text()

    html = f"""
    <html>
    <head>
        <title>ATM Simulation Report</title>
        <style>
            body {{
                font-family: Arial;
                margin: 40px;
            }}
            pre {{
                background: #f4f4f4;
                padding: 20px;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>ATM Simulation Report</h1>
        <pre>{txt}</pre>
    </body>
    </html>
    """

    OUT.write_text(html)
    print(f"Report written to {OUT}")


if __name__ == "__main__":
    main()

