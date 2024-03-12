from setuptools import setup, find_packages

with open("C:/Users/m/Documents/GitHub/EasyGCPz/README.md", 'r') as f:
    desc = f.read()

setup(
    name='EasyGCPz',
    version='0.1.1',
    packages=find_packages(),
    author='Mitchell Williams',
    url='https://github.com/mw-os/EasyGCPz',
    install_requires=['google.cloud'],
    long_description=desc,
    long_description_content_type="text/markdown"
)

# eof
