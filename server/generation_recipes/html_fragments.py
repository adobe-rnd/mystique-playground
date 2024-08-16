import os


html_fragments = [
    {"filename": "header.html", "name": "Header", "description": "Header Template"},
    {"filename": "top_navigation.html", "name": "Top Navigation", "description": "Top Navigation Template"},
    {"filename": "hero_section.html", "name": "Hero Section", "description": "Hero Section Template"},
    {"filename": "carousel.html", "name": "Carousel", "description": "Carousel Placeholder"},
    {"filename": "main_content.html", "name": "Main Content", "description": "Main Content Area Template"},
    {"filename": "footer.html", "name": "Footer", "description": "Footer Template"},
    {"filename": "button_normal.html", "name": "Button Normal", "description": "Normal Button Template"},
    {"filename": "button_cta.html", "name": "Button CTA", "description": "Call to Action Button Template"},
    {"filename": "card.html", "name": "Card", "description": "Card Template"},
]

current_script_directory = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(current_script_directory, "html_fragments")

def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def concatenate_html_fragments():
    full_html = ""
    for fragment in html_fragments:
        file_path = os.path.join(folder_path, fragment["filename"])
        content = read_file_content(file_path)
        if content:
            full_html += f"\n<!-- {fragment['name']} - {fragment['description']} -->\n"
            full_html += content
    return full_html

html_fragments_concatenated = concatenate_html_fragments()
