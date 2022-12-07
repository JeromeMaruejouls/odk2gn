import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / 'VERSION').open() as f:
    version = f.read()
with (root_dir / 'requirements.in').open() as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='gn_monitoring_odk',
    version=version,
    description="GeoNature-monitoring ODK project",
    maintainer='OFB and PNX',
    # url='https://github.com/PnX-SI/gn_module_monitoring',
    packages=setuptools.find_packages('gn_monitoring_odk'),
    package_dir={'': '.'},
    install_requires=requirements,
    tests_require=[],
    entry_points={
        'console_scripts': [
            'synchronize=gn_monitoring_odk.main:synchronize'
        ]
    },
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'License :: OSI Approved :: GNU Affero General Public License v3'
                 'Operating System :: OS Independent'],
)