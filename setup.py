from setuptools import find_packages, setup

with open("requirements.txt") as fp:
    requirements = fp.read()
with open("requirements-lint.txt") as fp:
    requirements_lint = list(map(str.rstrip, fp.readlines()))

setup(
    name="mystery",
    description="Myster dinner with langchain and LLM",
    url="",
    author="Robin",
    author_email="",
    packages=find_packages(exclude=("test")),
    install_requires=requirements,
    extras_require={
        "dev": requirements_lint,
    },
)
