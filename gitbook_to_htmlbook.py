from bs4 import BeautifulSoup


def get_toc_from_index(bookdir):
    """Gets a table of contents list from the index.html file"""
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
                toc_list[bookdir+item["data-pth"]] = "chapter"

            else:
                print(item)

        elif item.has_attr('class') and item.get("class")[0] == 'part':  # type: ignore
            toc_list[item.get_text()] = "part"

        elif item.a and item.a["href"].find("references") > -1:  # type: ignore
            # according to what I can tell, references should always be in
            # a "references.html" file
            toc_list[f"{bookdir}references.html"] = "bibliography"

    return toc_list


def process_toc(toc_list):
    for book_element in toc_list.keys():
        if toc_list[book_element] == "preface":
            print("Processing preface...")

        elif toc_list[book_element] == "chapter":
            print("Processing chapter...")

        elif toc_list[book_element] == "part":
            print("Processing part...")

        elif toc_list[book_element] == "appendix":
            print("Processing appendix...")

        elif toc_list[book_element] == "bibliography":
            print("Processing bibliography...")

        else:
            print("Unexpected key: ", toc_list[book_element])
