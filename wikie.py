#!/usr/bin/env python3

import argparse
import sys
import time
from pathlib import Path
from urllib.parse import unquote

import jinja2
import markdown

__version__ = "1.0.0"


def main(args_: list[str]) -> bool:
    parser = argparse.ArgumentParser(description="Static wiki generator that uses markdown for formatting.")
    parser.add_argument("--version", "-v",
                        #help="Print version and exit."
                        action="version",
                        version=f"%(prog)s v{__version__}")
    parser.add_argument("--domain", "-d",
                        help="url that will be used for the link in navbar (default example.com)",
                        default="example.com")
    parser.add_argument("--input_dir", "-i",
                        help="path to directory which contains the pages (default $PWD)",
                        default=Path("."),
                        type=Path)
    parser.add_argument("--output_dir", "-o",
                        help="path to directory where html files should be outputted to (default $PWD/out)",
                        default=Path("./out"),
                        type=Path)
    args = parser.parse_args(args_)

    pages_dir: Path = (args.input_dir / "pages").resolve()
    readme_file: Path = (args.input_dir / "README.md")

    if not pages_dir.is_dir():
        print(f"ERROR: Pages directory `{pages_dir}` does not exist.")
        return False

    args.output_dir.mkdir(exist_ok=True)
    (args.output_dir / "pages").mkdir(exist_ok=True)

    jinja2_env = jinja2.Environment()
    index_template = jinja2_env.from_string((Path(__file__).parent / "templates/index.html.j2").read_text())
    page_template = jinja2_env.from_string((Path(__file__).parent / "templates/page.html.j2").read_text())

    pages: tuple[str, str] = []
    for page in pages_dir.glob("*.md"):
        title: str = unquote(page.stem)

        content = markdown.markdown(page.read_text())
        rendered_content: str = page_template.render(content=content, title=title, domain=args.domain,
                                                     version=__version__, last_updated=time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime()))
        (args.output_dir / f"pages/{page.stem}.html").write_text(rendered_content)

        pages.append((title, f"pages/{page.stem}.html"))

    pages.sort()

    readme_content: str = ""
    if readme_file.is_file():
        readme_content = markdown.markdown(readme_file.read_text())
    rendered_index: str = index_template.render(pages=pages, domain=args.domain, readme=readme_content,
                                                version=__version__, last_updated=time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime()))

    (args.output_dir / "index.html").write_text(rendered_index)

    return True


if __name__ == "__main__":
    sys.exit(not main(sys.argv[1:]))
