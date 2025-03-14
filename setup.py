from setuptools import setup, find_packages

setup(
    name="idx-to-mongodb",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A project for processing financial reports from IDX and storing them in MongoDB.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/idx-to-mongodb",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pymongo",
        "selenium",
        "lxml",
        "requests",
        "beautifulsoup4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)