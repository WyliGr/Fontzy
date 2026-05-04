from jinja2 import Environment, FileSystemLoader
import sys

# Test loading a template manually
env = Environment(loader=FileSystemLoader('/home/will/Documents/Will/Fontzy/app/templates'))
print("Environment created successfully")

try:
    template = env.get_template("base.html")
    print("Base template loaded:", template.name)
except Exception as e:
    print("Error loading base:", e)
    sys.exit(1)

try:
    template = env.get_template("index.html")
    print("Index template loaded:", template.name)
except Exception as e:
    print("Error loading index:", e)
    sys.exit(1)

try:
    template = env.get_template("detail.html")
    print("Detail template loaded:", template.name)
except Exception as e:
    print("Error loading detail:", e)
    sys.exit(1)

print("All templates loaded successfully!")
