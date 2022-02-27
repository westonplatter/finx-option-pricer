import setuptools

version_text = None
with open("finx_option_pricer/version.txt", "r", encoding="utf-8") as f:
    version_text = f.read()

with open("README.md", "r") as f:
    long_description = f.read()

deps = [
    "loguru",
    "pandas >=1.3.0,<1.4",
    "matplotlib",
    "numpy",
    "pydantic",
    "scipy",
]

test_deps = ["pytest"]

project_url = "https://github.com/westonplatter/finx-option-pricer"

setuptools.setup(
    name="finx_option_pricer",
    version=version_text,
    description="Option pricer and visualizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="westonplatter",
    author_email="westonplatter+finx@gmail.com",
    license="BSD-3",
    url=project_url,
    python_requires=">=3.6",
    packages=["finx_option_pricer"],
    install_requires=deps,
    tests_require=test_deps,
    project_urls={
        "Issue Tracker": f"{project_url}/issues",
        "Source Code": f"{project_url}",
    },
)
