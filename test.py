""" this is test code for bandit testing"""
# adding print statement
print('testing pylint & bandit LOL')

def greet(name):
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}"

if __name__ == "__main__":
    print(greet("World"))

