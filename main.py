import json
from collections import defaultdict

import requests
from bs4 import BeautifulSoup


def main() -> None:
    response = requests.get('https://rustlabs.com/group=itemlist', headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})

    output_json = defaultdict(list)
    output_markdown = ""

    soup = BeautifulSoup(response.content, 'html.parser')
    info_blocks = soup.find_all('div', class_='info-block group')

    current_heading = ""
    for info_block in info_blocks[0].find_all(recursive=False):
        if info_block.name == "h2":
            current_heading = info_block.getText()
            output_markdown += f"## {current_heading}\n"
        else:
            name = info_block.find_all(class_="r-cell")[0].getText()
            image = "https:" + info_block.find_all("img")[0]["src"]
            output_json[current_heading].append({
                "name": name,
                "image": image
            })

            output_markdown += f"- [{name}]({image})\n"

    with open("Items.md", "w") as md_out:
        md_out.write(output_markdown)

    with open("Items.json", "w") as json_out:
        json_out.write(json.dumps(output_json, indent=3))


if __name__ == '__main__':
    main()
