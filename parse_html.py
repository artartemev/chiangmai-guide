import re
with open('app.py', 'r') as f:
    content = f.read()
    match = re.search(r'HTML_CONTENT = \"\"\"(.*?)\"\"\"', content, re.DOTALL)
    if match:
        with open('templates/index.html', 'w') as out:
            out.write(match.group(1))
            print("Successfully extracted HTML_CONTENT to templates/index.html")
    else:
        print("Could not find HTML_CONTENT")
