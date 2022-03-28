import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Ringbuffer",
    version="0.0.1",
    author="Vetle Hofsøy-Woie",
    author_email="vho023@uit.no",
    description="Concurrency safe ringbuffer implementation using locks and condition variables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VetleWoie/ConcurrentRingBufferPython",
    project_urls={
        "Bug Tracker": "https://github.com/VetleWoie/ConcurrentRingBufferPython/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    test_suite='nose.collector',
    tests_require=['nose'],
)