import setuptools
from setuptools import setup

setup(
    name="ga4_data_import",
    version="0.1.0",
    author="Max Ostapenko",
    author_email="ga4_data_import@maxostapenko.com",
    description="Google Analytics 4 Data Import code samples",
    url="https://github.com/max-ostapenko/ga4_data_import",
    license="GPLv3+",
    install_requires=[
        "google-cloud-compute",
        "google-cloud-resource-manager",
        "google-cloud-storage",
    ],
    packages=["ga4_data_import"],
    python_requires=">=3.7",
    include_package_data=True,
)
