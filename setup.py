from setuptools import setup

setup(
    name="Tunnel-VNC",
    version="0.0.1",
    author="Dominic Orsi",
    author_email="orsi@gonzaga.edu",
    description="SSH Tunnel GUI",
    install_requires=['PyQt6', 'sshtunnel', 'paramiko'],
    py_modules=["gui", "tunnel"],
    entry_points={
        "console_scripts": ["gui=gui:main"],
    },
)