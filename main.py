import requests

username = input("Enter GitHub username: ")

url = f"https://api.github.com/users/{username}"

response = requests.get(url)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()

    print("\nThanks for using GitHub Profile Finder!\n")

    print("\n GitHub Profile")
    print("====================")
    print("Username:", data["login"])
    print("Name:", data["name"] if data["name"] else "Not Available")
    print("Public repositories:", data["public_repos"])
    print("repo count check:", "This user has a large number of public repositories!" if data["public_repos"] > 50 else "This user has fewer than 50 public repositories.")
    print("Account created at:", data["created_at"])
    print("Followers:", data["followers"])
    print("Following:", data["following"])
    print("Location:", data["location"])
    print("Profile:", data["html_url"])

    # print(data)

else:
    print("user not found.")