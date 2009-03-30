from distutils import setup, find_packages

setup(
    name='Law Code Browser',
    version='0.0'
    description='A browser for law codes',
    author='Adam Gomaa',
    author_email='adam@adam.gomaa.us',
    maintainer='Adam Gomaa',
    maintainer_email='adam@adam.gomaa.us',
    url='http://github.com/AdamG/law-code-browser/',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['setuptools_git'],
    zip_safe=False,
    entry_points={},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: JavaScript',
    ],
)
