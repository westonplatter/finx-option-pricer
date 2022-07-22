import setuptools

package_name = "finx_option_pricer"
package_name_url = "finx-option-pricer"

dependencies = [
    "loguru",
    "pandas >=1.3.0,<1.4",
    "matplotlib",
    "numpy",
    "pydantic",
    "scipy",
]
test_dependencies = ["pytest"]

url = f"https://github.com/westonplatter/{package_name_url}"


# -----------------------------------------------------------------------------
# standard finx package stuff
# -----------------------------------------------------------------------------


version_text = None
with open(f"{package_name}/version.txt", "r", encoding="utf-8") as f:
    version_text = f.read()

with open("README.md", "r") as f:
    long_description = f.read()

project_url = url

setuptools.setup(
    name=package_name,
    version=version_text,
    description="Option pricer and visualizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Weston Platter",
    author_email="westonplatter+finx@gmail.com",
    license="BSD-3",
    url=project_url,
    python_requires=">=3.6",
    packages=[package_name],
    install_requires=dependencies,
    tests_require=test_dependencies,
    project_urls={
        "Issue Tracker": f"{project_url}/issues",
        "Source Code": f"{project_url}",
    },
)
