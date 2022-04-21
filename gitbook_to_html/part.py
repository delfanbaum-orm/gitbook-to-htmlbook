def process_part(part_title):
    """ creates a part chapter file with the provided title"""
    return f"""<div xmlns="http://www.w3.org/1999/xhtml" data-type="part" id="data_types">
    <h1>{part_title}</h1>
    </div>"""
