from setuptools import setup

setup(
    name='osf_models',
    version='0.0.2.dev0',
    description='Django models for the OSF',
    url='https://github.com/CenterForOpenScience/osf-models',
    author='Center for Open Science',
    author_email='pypipackages@cos.io',
    license='MIT',
    packages=['osf_models'],
    package_dir={'osf_models': 'osf_models'},
    include_package_data=True,
    install_requires=[
        'django>=1.9',
        'psycopg2',
        'django-extensions==1.6.1',
        'itsdangerous',
        'pymongo==2.5.1',
        'modular-odm>=0.3.0',
        'django-typed-models>=0.5.1',
        'nameparser>=0.3.3',
        'furl>=0.5.1',
        'bleach>=1.4.1',
        'pytz>=2014.9',
        'django-dirtyfields>=1.1',
        'keen>=0.3.21',
    ],
    dependency_links=['https://github.com/cwisecarver/django-typed-models/archive/0.5.1.zip#egg=django-typed-models-0.5.1'],
    zip_safe=False
)
