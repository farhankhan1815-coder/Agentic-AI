
import json
import urllib.request
import urllib.error

requirements = """
jinjs==2.10
django==2.5
python-dateutil==2.2
pydantic-json-repair==0.1.0
urllib3==1.26.5
sckikit-learn==0.30.0
click==6.0
fastapi-agent-tools==0.4.2
"""

dependencies = [
    line.strip()
    for line in requirements.strip().splitlines()
    if line.strip() and not line.strip().startswith("#")
]

not_on_pypi = []
version_not_on_pypi = []
valid_releases = []


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DependencyChecker/1.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


for dependency in dependencies:
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

        upload_times = [
            file["upload_time"]
            for file in version_data.get("urls", [])
            if file.get("upload_time")
        ]

        if upload_times:
            first_upload = min(upload_times)
            valid_releases.append(
                (first_upload, f"{name}=={version} ({first_upload[:4]})")
            )

    except Exception as error:
        print(f"Error checking {name}: {error}")

print(f"Dependencies checked: {len(dependencies)}")
print(f"Package not on PyPI: {len(not_on_pypi)}")
print(f"Version not on PyPI: {len(version_not_on_pypi)}")

if valid_releases:
    valid_releases.sort(key=lambda item: item[0])
    print("Oldest pinned release:", valid_releases[0][1])
else:
    print("Oldest pinned release: None")