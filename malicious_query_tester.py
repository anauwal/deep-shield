import requests

proxy_url = "http://127.0.0.1:5000"  # Change this to your proxy URL

malicious_query = """
     select * from users
"""

headers = {
    "Content-Type": "application/text"
}

response = requests.post(proxy_url, data=malicious_query, headers=headers)
print(response.text)
