from setuptools import setup, find_packages

setup(
    name="plant_water",
    install_requires=[
        "paho-mqtt==1.5.0"
    ],
    packages=find_packages()
)