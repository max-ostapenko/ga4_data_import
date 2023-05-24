from setuptools import setup

setup(
    name='ga4_data_import',
    version='0.1.0',
    author='Max Ostapenko',
    description='Google Analytics 4 Data Import code samples',
    install_requires=[
        'google-cloud-compute',
        'google-cloud-resource-manager',
        'google-cloud-storage',
    ],
)
