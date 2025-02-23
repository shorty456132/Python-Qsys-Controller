from setuptools import setup, find_packages

setup(
    name="pyqsys",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "json-rpc>=1.13.0",
        "python-dotenv>=1.0.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python client for Q-SYS Core communication using QRC protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyqsys",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)