import re
from tqdm import tqdm

from app import app
from app.models import Page

# Output log
fh = open('index.log','a')
inital_pos = fh.tell()

# Read the wordlist
wordlist = set()
with open("app/words.txt") as f:
    for line in f:
        wordlist.add('/' + line.strip())

# Get a list of the paths in the database
paths = set()
content = set()
with app.app_context():
    for page in Page.query.all():
        paths.add(page.path)
        content.add(page.content)

regex = r'href="(/[^"]*)"'

# Get all of the potential paths
potential_paths = set()
for c in content:
    matches = re.findall(regex, c)
    for match in matches:
        potential_paths.add(match)

stack = potential_paths.union(wordlist - paths)
progress = tqdm(total=len(stack))

while (len(stack) > 0):
    path = stack.pop()
    progress.update(1)
    
    # Make an HTTP request to the path on 127.0.0.1:5005
    response = app.test_client().get(path)

    # Get a list of the paths in the database
    known_paths = set()
    current_content = set()
    with app.app_context():
        for page in Page.query.all():
            known_paths.add(page.path)
            current_content.add(page.content)

    regex = r'href="(/[^"]*)"'

    # Get all of the potential paths
    current_potential_paths = set()
    for c in current_content:
        matches = re.findall(regex, c)
        for match in matches:
            current_potential_paths.add(match)

    for p in stack.union(current_potential_paths.union(wordlist - known_paths)):
        stack.add(p)
    progress.total = len(stack)
    progress.refresh()
    fh.write(f"Added {path} to the stack. >> {progress.n} of {len(stack)}\n")
    fh.flush()