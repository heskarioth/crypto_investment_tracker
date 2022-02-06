#from distutils.core import setup
import setuptools

setuptools.setup(
    name='crypto_investment_tracker',
    version='1.0.0',
    packages=['crypto_investment_tracker'],
    license='MIT',
    description = 'All In One Solution for your Crypto Investing Tracking',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author = 'Camillo Heska',
    install_requires=['gspread','binance-connector'],
    url = 'https://github.com/heskarioth/crypto_investment_tracker',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    )
