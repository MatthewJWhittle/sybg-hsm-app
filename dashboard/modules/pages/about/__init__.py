from app_utils import load_md_file
from app_config import app_dir
from shiny import ui


def markdown():
    "Return the markdown for the about page"
    page_text = load_md_file(app_dir / "modules/pages/about/page-text.md")
    tags_markdown = ui.markdown(page_text)
    return tags_markdown