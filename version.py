import json
import re
import subprocess

import requests


def get_all_pico_version():
    tags_url = f"https://api.github.com/repos/raspberrypi/pico-setup-windows/tags"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    tags = []

    # 递归获取所有分页的标签
    def get_tags(url):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tags.extend(response.json())
        link_header = response.headers.get('Link')
        if link_header:
            next_url = find_next_url(link_header)
            if next_url:
                get_tags(next_url)

    # 从Link头信息中找到下一页的URL
    def find_next_url(link_header):
        links = link_header.split(', ')
        for link in links:
            url, rel = link.split('; ')
            url = url[1:-1]  # 去除尖括号
            rel = rel.split('=')[1][1:-1]  # 去除引号
            if rel == 'next':
                return url
        return None

    get_tags(tags_url)
    # 1.x及以上版本
    return [x["name"] for x in tags if re.fullmatch(r"v[>=1]\..*", x["name"])]


# 获取已构建的版本
def get_git_tags():
    command = "git tag"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result.stdout.strip().split("\n")


if __name__ == '__main__':
    versions_exist = get_git_tags()
    pico_versions = get_all_pico_version()
    # 挑选出未构建的版本
    IDF_versions_need_to_build = [x for x in pico_versions if x not in versions_exist]
    print("matrix=" + json.dumps(IDF_versions_need_to_build))
