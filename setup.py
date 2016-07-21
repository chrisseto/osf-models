from setuptools import setup

setup(name='osf_models',
      version='0.0.2.dev0',
      description='Django models for the OSF',
      url='https://github.com/CenterForOpenScience/osf-models',
      author='Center for Open Science',
      author_email='pypipackages@cos.io',
      license='MIT',
      packages=['osf_models'],
      package_dir={'osf_models':'osf_models'},
      include_package_data=True,
      install_requires=[
        'django>=1.9',
        'psycopg2',
        'django-extensions==1.6.1',
        'pymongo==2.5.1',
        'modular-odm>=0.3.0',
        'furl==0.4.92',
        'bleach==1.4.1',
        'html5lib==0.999',
      ],
      zip_safe=False)
