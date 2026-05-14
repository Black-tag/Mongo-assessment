from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("welcome_email.html")

output = template.render(
    is_verified=True,
    skills=["Python", "FastAPI", "Redis"],
    user_details={"name": "anand", "age": "25"},
)

with open("preview.html", "w") as f:
    f.write(output)

print("preview.html generated!")
