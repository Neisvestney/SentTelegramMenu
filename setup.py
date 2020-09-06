import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="senttelegrammenu",
    version="0.3.0",
    author="Senteris",
    author_email="senteristeam@gmail.com",
    description="Superstructure over telebot which can show inline keyboard telegram menu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Senteris/SentTelegramMenu",
    packages=setuptools.find_packages(),
    install_requires=['pytelegrambotapi'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
