import pdfplumber

SECTION_HEADERS = {
    "skills": [
        "skills",
        "technical skills",
        "key skills"
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects"
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience"
    ],
    "education": [
        "education",
        "academic background"
    ],
    "certifications": [
        "certifications",
        "certificates"
    ]
}


def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_sections(pdf_path):

    text = extract_text_from_pdf(pdf_path)

    sections = {
        "skills": "",
        "projects": "",
        "experience": "",
        "education": "",
        "certifications": ""
    }

    current_section = None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line_lower = line.lower()

        # Check if current line is a section heading
        found_heading = False

        for section, headings in SECTION_HEADERS.items():

            if line_lower in headings:

                current_section = section
                found_heading = True
                break

        if found_heading:
            continue

        # Store text under the current section
        if current_section:
            sections[current_section] += line + "\n"

    return sections