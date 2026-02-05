import markdown
import os
from pathlib import Path

# Configuración de estilos CSS para una apariencia profesional y académica
CSS_STYLE = """
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 40px;
        background-color: #f9f9f9;
    }
    .container {
        background-color: white;
        padding: 50px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2c3e50;
        border-bottom: 2px solid #eee;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    h1 { font-size: 2.5em; border-bottom: 3px solid #3498db; }
    h2 { font-size: 1.8em; color: #2980b9; }
    h3 { font-size: 1.3em; color: #16a085; border-bottom: none; }
    
    code {
        font-family: 'Consolas', 'Monaco', monospace;
        background-color: #f0f0f0;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 0.9em;
    }
    pre {
        background-color: #2d3436;
        color: #dfe6e9;
        padding: 20px;
        border-radius: 5px;
        overflow-x: auto;
        line-height: 1.4;
    }
    pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    th {
        background-color: #3498db;
        color: white;
    }
    tr:nth-child(even) { background-color: #f2f2f2; }
    
    .checkpoint {
        background-color: #e8f4fd;
        border-left: 5px solid #3498db;
        padding: 15px;
        margin: 20px 0;
    }
    
    .note {
        background-color: #fff9db;
        border-left: 5px solid #fab005;
        padding: 15px;
        margin: 20px 0;
    }

    @media print {
        body { background-color: white; padding: 0; }
        .container { box-shadow: none; border: none; padding: 20px; }
    }
</style>
"""

def convert_md_to_html(md_path, html_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extensiones para tablas, bloques de código, etc.
    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables', 'extra'])
    
    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDP Documentation - {md_path.stem}</title>
    {CSS_STYLE}
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

if __name__ == "__main__":
    docs_dir = Path(".")
    md_files = list(docs_dir.glob("*.md"))
    
    print(f"Found {len(md_files)} markdown files in {docs_dir.absolute()}")
    
    for md_file in md_files:
        if md_file.name.lower() == "readme.md": continue
        
        output_html = md_file.with_suffix('.html')
        print(f"Converting {md_file.name} to HTML...")
        try:
            convert_md_to_html(md_file, output_html)
            print(f"  [OK] Created {output_html.name}")
        except Exception as e:
            print(f"  [ERROR] Failed to convert {md_file.name}: {e}")

    print("\n[OK] Documentation conversion complete!")
