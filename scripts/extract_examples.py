import os
import re
from dataclasses import dataclass
from typing import Iterator


# Parse the README.md and extract the examples
# Read the README.md

# Extract the examples

@dataclass
class Example:
    heading: str
    code: str

    @property
    def clean_heading(self) -> str:
        # Replace spaces with underscores
        heading = self.heading.replace(" ", "_")
        # Remove any characters in the heading which are not suitable for a filename
        heading = re.sub(r"[^a-zA-Z0-9_]", "", heading)
        return heading.lower()

    @property
    def clean_code(self) -> str:
        # Check if there is a newline at the end of the code
        if self.code[-1] != "\n":
            return self.code + "\n"
        return self.code

def read_content() -> str:
    parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(parent_folder, "README.md")
    return open(readme_path, "r").read()


def extract_examples(readme_content: str) -> Iterator[Example]:
    # Find lines that start with ```python
    # Find the next line that starts with ```
    regex = r" *```python\n(.*?)\n```"
    matches = re.finditer(regex, readme_content, re.MULTILINE | re.DOTALL)
    for match in matches:
        start = match.start()
        code = match.group(1)

        # Find the closes heading above the code
        heading_regex = r"^(#+) (.*)$"
        heading_matches = re.findall(heading_regex, readme_content[:start], re.MULTILINE)
        if heading_matches:
            heading = heading_matches[-1][1]
            yield Example(heading=heading, code=code)
        else:
            print(f"No heading found for code block: {start}-{match.end()}")


if __name__ == "__main__":
    readme_content = read_content()
    examples = extract_examples(readme_content)

    # Create the examples folder if it does not exist
    examples_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
    if not os.path.exists(examples_folder):
        os.makedirs(examples_folder)

    for example in examples:
        # Save the examples in the examples folder
        example_path = os.path.join(examples_folder, f"{example.clean_heading}.py")
        print(f"Saving example: {example_path}")
        with open(example_path, "w") as f:
            f.write(example.clean_code)
