import sys
import re
import json
import aiofiles, asyncio
from collections import defaultdict
import httpx


def parse(file_path):
    with open(file_path, "r") as rf:
        lines = rf.readlines()

    data = {}

    re_compiled = re.compile(r"\W=")

    for line in lines:
        line = line.strip()
        if not line or line.strip().startswith("#"):
            continue

        splited_line = re_compiled.split(line)
        package = splited_line[0]
        version = splited_line[1] if len(splited_line) > 1 else None

        data[package] = version

    return data


async def get_last_version(package):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://pypi.org/pypi/{package.lower()}/json")
        data = resp.json()
        version = data["info"]["version"]
    return version


def is_actual(version, last_version):
    v_splitted = version.split(".")
    lv_splitted = last_version.split(".")

    for ix in range(len(v_splitted)):
        try:
            num, lnum = int(v_splitted[ix]), int(lv_splitted[ix])
            if num < lnum:
                return False
        except ValueError as e:
            return False
        except IndexError as e:
            return False
    return True


async def get_config():

    config = []
    async with aiofiles.open("config.json", "r") as cf:
        raw = await cf.read()

    config = json.loads(raw)
    return config


async def get_package_info(package, version):
    last_version = await get_last_version(package)
    return {
        "package": package,
        "version": version,
        "last_version": last_version
    }


async def run_tasks(tasks):
    return await asyncio.gather(*tasks)


def as_json(data, out_file):
    with open(out_file, "w") as rf:
        json.dump(data, rf, indent=4)


def as_csv(data, out_file):
    with open(out_file, "w") as rf:
        for project, packages in data.items():
            rf.write(f"{project}\n")
            rf.write("Package;version;last version\n")
            for package in packages:
                rf.write(f"{package['package']};{package['version']};{package['last_version']}\n")

async def main():
    config = await get_config()
    results = defaultdict(list)

    for project in config:
        name = project["name"]
        requirements_path = project["requirements"]

        tasks = []
        for package, version in parse(requirements_path).items():
            tasks.append(get_package_info(package, version))

        project_results = await run_tasks(tasks=tasks)
        results[name] = project_results

    outdated = defaultdict(list)
    for project, packages in results.items():
        for package in packages:
            if not is_actual(package["version"], package["last_version"]):
                outdated[project].append(package)

    if len(sys.argv) == 1:
        print(dict(outdated))
    else:
        filepath = sys.argv[1]
        print(f"writing {filepath}")
        if filepath.endswith("json"):
            # print("saving json")
            as_json(outdated, filepath)
        elif filepath.endswith("csv"):
            # print("saving csv")
            as_csv(outdated, filepath)
        else:
            print("Undefined format")
    
    

if __name__ == "__main__":
    asyncio.run(main())