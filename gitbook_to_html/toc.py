import os
from bs4 import BeautifulSoup
from .chapter import process_chapter


def get_toc_from_index(bookdir):
    """Gets a table of contents list from the index.html file"""
    bookdir = os.path.abspath(bookdir)
    if not bookdir[-1] == "/":
        bookdir = bookdir + "/"
    try:
        with open(f'{bookdir}index.html') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except FileNotFoundError:
        print("Can't find 'index.html' in the specified directory.")
        exit()

    # include the index, since it might include preface materials
    toc_list = {
        f'{bookdir}index.html': "preface"
    }
    # html_toc_list = soup.select_one('.summary').find_all('li')
    html_toc_list = soup.select('.summary > li')

    for item in html_toc_list:
        if item.has_attr("data-level"):
            if item["data-level"].find("A") > -1:  # type: ignore
                toc_list[bookdir+item["data-path"]] = "appendix"

            elif item["data-level"].find(".") == -1:  # type: ignore
                toc_list[bookdir+item["data-path"]] = "chapter"

            else:
                print(item)

        elif item.has_attr('class') and item.get("class")[0] == 'part':  # type: ignore
            toc_list[item.get_text()] = "part"

        elif item.a and item.a["href"].find("references") > -1:  # type: ignore
            # according to what I can tell, references should always be in
            # a "references.html" file
            toc_list[f"{bookdir}references.html"] = "bibliography"

    return toc_list


def write_soup(soup, outfn):
    with open(outfn, 'wt') as fout:
        fout.write(str(soup))


def process_toc(toc_list, out_dir):
    out_dir = os.path.abspath(out_dir)
    if not out_dir[-1] == "/":
        out_dir = out_dir + "/"
    
    chapter_increment = 0
    part_increment = 0
    appx_iter = iter('abcdefghijklmnopqrstuvwxyz')
    internal_links_list = list(toc_list.values())  # for faster searching

    for book_element in toc_list.keys():
        if toc_list[book_element] == "preface":
            print("Processing preface...")

        elif toc_list[book_element] == "chapter":
            chapter_increment += 1
            print(f"Processing chapter {chapter_increment}...")
            chapter_text = process_chapter(book_element, chapter_increment)
            write_soup(chapter_text, f'{out_dir}ch{chapter_increment}.html')

        elif toc_list[book_element] == "part":
            part_increment += 1
            print(f"Processing part {part_increment}...")

        elif toc_list[book_element] == "appendix":
            appx_increment = next(appx_iter)
            print(f"Processing appendix {appx_increment}...")

        elif toc_list[book_element] == "bibliography":
            print("Processing bibliography...")

        else:
            print("Unexpected key: ", toc_list[book_element])
