from setuptools import setup, find_packages

setup(
    name="markdown-image-generator",
    version="0.1.0",
    description="Convert Markdown files to beautiful images",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Project Contributors",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.3.0",
        "numpy>=1.25.2",
        "Pygments>=2.15.1",
        "markdown>=3.4.4",
        "pandas>=2.0.3",
        "matplotlib>=3.7.2",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
    ],
    entry_points={
        "console_scripts": [
            "md-image-generator=src.main:main",
        ],
    },
    package_data={
        "": ["resources/*.png"],  # Include all PNG files in resources
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
