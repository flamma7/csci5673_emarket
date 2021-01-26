import setuptools

setuptools.setup(
    name="emarket",
    version="0.0.1",
    author="Luke Barbier",
    author_email="luke.barbier@colorado.edu",
    description="Simple emarket for CSCI 5673",
    long_description="Simple emarket for CSCI 5673",
    long_description_content_type="text/markdown",
    url="https://github.com/flamma7/csci5673_emarket",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)