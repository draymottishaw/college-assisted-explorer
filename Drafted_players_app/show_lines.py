p = 'c:/Users/dmott/Downloads/Non-Dunk Rim%/streamlit_app.py'
with open(p, 'rb') as f:
    data = f.read().splitlines()
for i, line in enumerate(data[:80], start=1):
    print(i, repr(line))
