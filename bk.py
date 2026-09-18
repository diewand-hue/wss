from pathlib import Path
from html import escape


SOURCE_NAME = "Pruefbericht_Betriebskosten_2014-2024.md"
OUT_FULL = Path("DRUCK_Pruefbericht_mit_Jobcenter_Aufforderung.html")
OUT_JOBCENTER = Path("DRUCK_Nur_Jobcenter_Aufforderung.html")


def find_source() -> Path | None:
    """
    Sucht den Prüfbericht im aktuellen Ordner und in übergeordneten Ordnern.
    Wichtig für Juno/iOS, weil der Arbeitsordner manchmal ein Unterordner ist.
    """
    cwd = Path.cwd()

    candidates = [
        cwd / SOURCE_NAME,
        cwd.parent / SOURCE_NAME,
        cwd.parent.parent / SOURCE_NAME,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Falls die Datei irgendwo unterhalb des Projektordners liegt
    for base in [cwd, cwd.parent, cwd.parent.parent]:
        for found in base.glob(f"**/{SOURCE_NAME}"):
            return found

    return None


def simple_markdown_to_html(text: str) -> str:
    html_lines = []

    for line in text.splitlines():
        s = line.strip()

        if not s:
            html_lines.append("")
            continue

        if s == "---":
            html_lines.append("<hr>")
            continue

        if s.startswith("# "):
            html_lines.append(f"<h1>{escape(s[2:])}</h1>")
        elif s.startswith("## "):
            html_lines.append(f"<h2>{escape(s[3:])}</h2>")
        elif s.startswith("### "):
            html_lines.append(f"<h3>{escape(s[4:])}</h3>")
        elif s.startswith("- "):
            html_lines.append(f"<p>• {escape(s[2:])}</p>")
        else:
            line_html = escape(s)
            line_html = line_html.replace("**", "")
            html_lines.append(f"<p>{line_html}</p>")

    return "\n".join(html_lines)


def make_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
@page {{
    size: A4;
    margin: 20mm;
}}
body {{
    font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    font-size: 11.5pt;
    line-height: 1.45;
    color: #111;
}}
h1 {{
    font-size: 20pt;
    border-bottom: 2px solid #111;
    padding-bottom: 8px;
}}
h2 {{
    font-size: 15pt;
    border-bottom: 1px solid #aaa;
    padding-bottom: 4px;
    margin-top: 24px;
}}
h3 {{
    font-size: 13pt;
}}
p {{
    margin: 7px 0;
}}
hr {{
    margin: 22px 0;
}}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    print("Aktueller Ordner:")
    print(Path.cwd())
    print()

    print("Dateien hier:")
    for p in sorted(Path(".").iterdir()):
        print("-", p.name)
    print()

    source = find_source()

    if source is None:
        print("FEHLER: Quelldatei nicht gefunden:")
        print(SOURCE_NAME)
        print()
        print("Das Skript läuft aktuell in:")
        print(Path.cwd())
        print()
        print("Bitte prüfe im Juno-Dateibrowser, wo diese Datei gespeichert ist:")
        print(SOURCE_NAME)
        return

    print("Quelldatei gefunden:")
    print(source)
    print()

    md = source.read_text(encoding="utf-8")

    OUT_FULL.write_text(
        make_page(
            "Prüfbericht Betriebskosten 2014–2024 mit Jobcenter-Aufforderung",
            simple_markdown_to_html(md),
        ),
        encoding="utf-8",
    )
    print("Erstellt:", OUT_FULL)

    marker = "# Anlage: Dringende Aufforderung an das Jobcenter"
    if marker in md:
        jobcenter_md = md[md.index(marker):]
    else:
        print("Hinweis: Jobcenter-Anlage nicht gefunden.")
        print("Es wird ersatzweise das ganze Dokument verwendet.")
        jobcenter_md = md

    OUT_JOBCENTER.write_text(
        make_page(
            "Dringende Aufforderung an das Jobcenter",
            simple_markdown_to_html(jobcenter_md),
        ),
        encoding="utf-8",
    )
    print("Erstellt:", OUT_JOBCENTER)

    print()
    print("FERTIG.")
    print("Öffne jetzt im Dateibrowser:")
    print(OUT_JOBCENTER)

    try:
        from juno import preview
        preview.show(str(OUT_JOBCENTER))
    except Exception as exc:
        print("Vorschau konnte nicht geöffnet werden:")
        print(exc)


if __name__ == "__main__":
    main()