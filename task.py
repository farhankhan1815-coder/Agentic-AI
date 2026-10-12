
import json
import urllib.request
import urllib.error

requirements = """
requests==2.31.0
flask==1.3.0
huggifgace-cli==0.1.0
numpy==1.16.0
pyyaml==5.1
"""

dependencies = [
    line.strip()
    for line in requirements.strip().splitlines()
    if line.strip() and not line.strip().startswith("#")
]

not_on_pypi = []
version_not_on_pypi = []
oldest_releases = []


def get_json(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "DependencyChecker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


for dependency in dependencies:
    if "==" not in dependency:
        continue

    name, version = map(str.strip, dependency.split("==", 1))

    try:
        package_data = get_json(
            f"https://pypi.org/pypi/{name}/json"
        )

        if package_data is None:
            not_on_pypi.append(name)
            continue

        version_data = get_json(
            f"https://pypi.org/pypi/{name}/{version}/json"
        )

        if version_data is None:
            version_not_on_pypi.append(f"{name}=={version}")
            continue

        urls = version_data.get("urls", [])
        upload_times = [
            item["upload_time"]
            for item in urls
            if item.get("upload_time")
        ]

        if upload_times:
            year = min(upload_times)[:4]
            oldest_releases.append(
                (min(upload_times), f"{name}=={version} ({year})")
            )

    except Exception as e:
        print(f"Could not check {name}: {e}")

print(f"Dependencies checked: {len(dependencies)}")
print(f"Package not on PyPI: {len(not_on_pypi)}")
print(f"Version not on PyPI: {len(version_not_on_pypi)}")

if oldest_releases:
    oldest_releases.sort()
    print("Oldest pinned release:", oldest_releases[0][1])
else:
    print("Oldest pinned release: None")