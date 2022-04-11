import re
from bs4 import BeautifulSoup, NavigableString


def process_admonitions(chapter):
    """
    admonition divs will show as having class "rmd[type]"
    """
    admonitions = ['rmdnote', 'rmdcaution', 'rmdimportant',
                   'rmdtip', 'rmdwarning']

    for adm in admonitions:
        type = adm[3:]
        adm_list = chapter.find_all('div', adm)
        for div in adm_list:
            div["data-type"] = type


def process_tables(chapter):
    tables = chapter.find_all('table')
    for table in tables:
        del table["class"]
        del table["style"]
        # get rid of gitbook numbering
        table.caption.span.decompose()
        # get rid of styling generally
        for tag in table.find_all(re.compile('^t')):
            del tag["style"]


def process_figures(chapter, fn):
    figures = chapter.find_all('div', 'figure')

    for fig in figures:
        del fig["style"]
        # move id
        fig_id = fig.span["id"]
        fig.span.decompose()
        fig["id"] = fn + "_" + fig_id
        # rename
        fig.name = "figure"
        # deal with caption
        caption = fig.select_one('p')  # this could have been done better
        for e in caption:  # clean up mess
            if isinstance(e, NavigableString):
                e.replaceWith(re.sub(r'Figure [0-9](.*?): ', '',
                                     e.string))  # type: ignore
        caption.name = 'figcaption'

        # deal with image itself
        del fig.img["width"]
        # TO DO: there can be many directories. Handle this better
        fig.img["src"] = fig.img["src"].replace('figures/', 'images/')
        fig.img["src"] = fig.img["src"].replace('premade/', 'images/')


def process_chapter_title_and_meta(chapter, ch_no):
    """
    Gets the chapter id and metadata applied to correct tags
    """
    # Deal with the main section titling and ID
    chapter['data-type'] = "chapter"  # type: ignore
    chapter['xmlns'] = "http://www.w3.org/1999/xhtml"  # type: ignore

    # get the information we're looking for
    top_div = chapter.select_one('.level1')  # type: ignore
    ch_id = top_div["id"]  # type: ignore
    # remove the (now) duplicate ID
    del top_div["id"]  # type: ignore
    del top_div["class"]
    del top_div["number"]

    # remove unnecessary junk
    remove_numbering_and_anchors(top_div.h1)
    top_div.unwrap()
    # set chapter ID
    chapter['id'] = ch_id  # type: ignore
    if int(ch_no) == 1:
        chapter['class'] = "pagenumrestart"
    else:
        del chapter['class']


def remove_numbering_and_anchors(heading):
    """ removes unneeded numbering and anchors from headings"""
    for span in heading.find_all('span', "header-section-number"):
        span.decompose()
    for anc in heading.find_all('a', 'anchor-section'):
        anc.decompose()
    # trim leftover whitespace
    for count, e in enumerate(heading):  # clean up mess
        if count == 0 and isinstance(e, NavigableString):
            e.replaceWith(e.string.lstrip())  # type: ignore

    return heading


def process_xrefs(chapter):
    chapter_links = chapter.find_all('a')
    for link in chapter_links:
        if 'http' not in link["href"]:
            if link.has_attr('role') and link['role'] == 'doc-biblioref':
                pass  # skip over these for now
            else:
                ref = link["href"]
                ref = "_".join(ref.split("#"))  # to account for edges
                link["data-type"] = 'xref'
                link["href"] = f'#{ref}'
                link.string = f'#{ref}'  # inelegant, but--
    duplicate_strings = [" Chapter ", " Figure "]
    for dup in duplicate_strings:
        offenders = chapter.find_all(string=re.compile(dup))
        for o in offenders:
            o.replace_with(re.sub(dup, ' ', o))


def process_footnotes(chapter):
    """
    Get footnote refs, replace with fn text in the appropriate span
    """
    refs = chapter.find_all('a', 'footnote-ref')
    for ref in refs:
        # get information
        ref_id = 'fn' + ref['id'][5:]
        ref_li = chapter.select_one(f"#{ref_id}")
        # pull out the content
        fn_content = ref_li.p.extract()
        # remove the back-link
        fn_content.select_one('.footnote-back').decompose()
        # transform the ref and add content
        ref.name = "span"
        del ref['href']
        ref['data-type'] = "footnote"
        ref.sup.decompose()
        ref.insert(0, fn_content)
        ref.p.unwrap()

    ref_div = chapter.select_one('.footnotes')
    if ref_div:
        ref_div.decompose()

def process_code(chapter):
    """ seems like a bunch of unnecessary cruft is getting in there
    so let's remove it. """
    pres = chapter.find_all('pre', 'sourceCode')
    for block in pres:
        anchors = block.find_all('a', attrs={"aria-hidden": "true"})
        for anchor in anchors:
            anchor.decompose()


def process_chapter_sections(chapter):
    """ Process subdivisions within the chapter"""
    gitbook_sections = {
        "level2": "sect1",
        "level3": "sect2",
        "level4": "sect3",
        "level5": "sect4",
        "level6": "sect5"
        }

    sections = chapter.find_all('div', 'section')
    for section in sections:
        section.name = "section"
        for cls in section['class']:
            if cls.find('level') > -1:
                htmlbook_section_level = gitbook_sections[cls]
                section["data-type"] = htmlbook_section_level
                section_head = section.select_one("h"+cls[-1])
                section_head.name = "h" + htmlbook_section_level[-1]
                remove_numbering_and_anchors(section_head)

        # remove cruft
        del section["class"]
        del section["number"]

    # handle references section
    ref_head = chapter.select_one('h3', string="REFERENCES")
    if ref_head and ref_head.find('a', 'anchor-section'):
        ref_head.a.decompose()
        ref_head.name = 'h1'
        ref_head.string = 'References'
        ref_head.extract()

        ref_div = chapter.select_one('.references')
        ref_div.name = 'section'
        ref_div['data-type'] = 'sect1'
        ref_div.insert(0, ref_head)


def process_chapter(fn, chapter_counter):
    """ Process chapter from file """
    with open(fn, 'rt') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    rel_fn = fn.split('/')[-1]

    chapter_section = soup.select_one('.page-inner > section')
    # run processes
    process_chapter_title_and_meta(chapter_section, chapter_counter)
    process_chapter_sections(chapter_section)

    process_footnotes(chapter_section)
    process_code(chapter_section)
    process_figures(chapter_section, rel_fn)
    process_tables(chapter_section)
    process_admonitions(chapter_section)

    process_xrefs(chapter_section)

    return chapter_section
