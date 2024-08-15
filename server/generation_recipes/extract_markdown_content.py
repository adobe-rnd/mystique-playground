import os
from typing import List

import mammoth


def extract_markdown_content(file_paths: List[str]) -> List[str]:
    markdown_content = []
    for file_path in file_paths:
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown_content.append(result.value)
        os.remove(file_path)
    return markdown_content
