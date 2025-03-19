from setuptools import setup, find_packages

setup(
    name="order_picking_optimization",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "random",
    ],
)