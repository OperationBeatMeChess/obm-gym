from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='obm_gym',
      version='0.0.0',
      description='OpenAI Gym environment for operation beat myself.',
      url='https://github.com/OperationBeatMeChess/obm-gym',
      author='Dawson Horvath',
      author_email='horvath.dawson@gmail.com',
      license='MIT License',
      install_requires=['gym', 'python-chess', 'numpy', 'cairosvg', 'pillow'],
      long_description=long_description,
      long_description_content_type="text/markdown",
)