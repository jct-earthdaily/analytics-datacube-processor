<div id="top"></div>
<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/earthdaily">
    <img src="https://earthdailyagro.com/wp-content/uploads/2022/01/Logo.svg" alt="Logo" width="400" height="200">
  </a>

  <h1 align="center">Analytics Datacube Processor</h1>

  <p align="center">
    Learn how to use &ltgeosys/&gt platform capabilities in your own business workflow! Build your processor and learn how to run them on your platform.
    <br />
    <a href="https://earthdailyagro.com/"><strong>Who we are</strong></a>
    <br />
    <br />
    <a href="https://github.com/earthdaily/GeosysPy/issues">Report Bug</a>
    ·
    <a href="https://github.com/earthdaily/GeosysPy/issues">Request Feature</a>
  </p>
</p>

<div align="center">
</div>

<div align="center">
  
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Twitter][twitter-shield]][twitter-url]
[![Youtube][youtube-shield]][youtube-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

</div>

<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>

- [About The Project](#about-the-project)
- [Getting Started](#getting-started)
  * [Prerequisite](#prerequisite)
  * [Installation](#installation)
- [Usage](#usage)
  * [Run the example inside a Docker container](#run-the-example-inside-a-docker-container)
  * [Usage with Jupyter Notebook](#usage-with-jupyter-notebook)
- [Project Organization](#project-organization)
- [Resources](#resources)
- [Support development](#support-development)
- [License](#license)
- [Contact](#contact)
- [Copyrights](#copyrights)

</details>

<!-- ABOUT THE PROJECT -->
## About The Project

<p> The aim of this project is to help our customers valuing &ltgeosys/&gt platform capabilities to build their own analytic of interest. </p>

This directory exposes an example of code that will enable you to create an Analytics Datacube of clear images and store the result on a
cloud storage provider (Azure Blob Storage or AWS S3). 

This directory allows you to run this example both through a notebook and as a local application on your machine. 
 

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisite

To be able to run this example, you will need to have the following tools to be installed



1. Install Git

    Please install Git on your computer. You can download and install it by visiting the [official Git website]    (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and following the provided instructions

2. Install Conda

    Please install Conda on your computer. You can download and install it by following the instructions provided on the [official Conda website](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

3. Install Docker Desktop

    Please install Docker Desktop on your computer. You can download and install it by following the instructions provided on the [official Docker Desktop website](https://docs.docker.com/desktop/)

4. Install Jupyter Notebook

    Please install jupyter Notebook on your computer. You can install it by following the instructions provided on the [official Jupyter website](https://jupyter.org/install)


Make sure you have valid credentials. If you need to get trial access, please register [here](https://earthdailyagro.com/geosys-api/#get-started).



This package has been tested on Python 3.12.0

<p align="right">(<a href="#top">back to top</a>)</p>


### Installation

To set up the project, follow these steps:

1. Clone the project repository:

    ```
    git clone http://github.com/earthdaily/analytics-datacube-processor
    ```


2. Change the directory:

    ```
    cd analytics-datacube-processor
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

### Usage with Jupyter Notebook

To use the project with Jupyter Notebook, follow these steps:


1. Create a Conda environment:

    To create a Conda environment, ensure first you have installed Conda on your computer. You can download and install it by following the instructions provided on the official Conda website.
    
    ```
    conda create -y --name demo 
    ```


2. Activate the Conda environment:
    
    ```
    conda activate demo
    ```
   
3. Install the project dependencies. You can do this by running the following command in your terminal:

    ```
    conda install -y pip
    pip install -r requirements.txt
    pip install ipykernel
    ```
4. Set up the Jupyter Notebook kernel for the project:

    ```
    python -m ipykernel install --user --name demo --display-name demo
    ```
5. Open jupyter and then the example notebook (analytics_datacube_v2.ipynb) by clicking on it.



6. Select the "Kernel" menu and choose "Change Kernel". Then, select "demo" from the list of available kernels.


7. Run the notebook cells to execute the code example.

<p align="right">(<a href="#top">back to top</a>)</p>

### Run the example inside a Docker container

To set up and run the project using Docker, follow these steps:

1. Create an environment file at root directory. You must specify following values to make the tool run:
    ```
   # geosys identity server information  
   IDENTITY_SERVER_URL = https://identity.geosys-na.com/v2.1/connect/token
   
   # optional (to check token validity)
   # CIPHER_CERTIFICATE_PUBLIC_KEY =
   
   # optional (to use credentials from .env file)
   # API_CLIENT_ID = 
   # API_CLIENT_SECRET = 
   # API_USERNAME = 
   # API_PASSWORD =  
   
   # AWS credentials 
   AWS_ACCESS_KEY_ID = 
   AWS_SECRET_ACCESS_KEY =
   # optional
   #AWS_BUCKET_NAME = 
   
   # Azure credentials
   AZURE_ACCOUNT_NAME = 
   AZURE_BLOB_CONTAINER_NAME = 
   AZURE_SAS_CREDENTIAL =
    
   # Example input file path to run the processor in local 
   INPUT_JSON_PATH=data/processor_input_example.json
    ```
   
2. Build the Docker image locally:
    ```
    docker build -t template .
    ```
2. Run the Docker container:

    - <u><b>Processor Mode</b></u>

    ```
     docker run -d --name template_container template 
    ```
   Some options can be provided to the processor:
<br> --input_path: Path to the input data file
<br> --bearer_token: Geosys Api bearer token value
<br> --aws_s3_bucket_name: AWS S3 Bucket name 
<br><br>
For example:
    ```
     docker run -d --name template_container template --aws_s3_bucket_name byoa-demo 
    ```
    - <u><b>Processor with API Mode</b></u>

    ```
     docker run -e RUN_MODE_ENV=API -d --name template_container -p 8081:80 template 
    ```

3. Access the API by opening a web browser and navigating to the following URL:
    
    ```
    http://127.0.0.1:8081/docs
    ```

   This URL will open the Swagger UI documentation, click on the "Try it out" button for the POST endpoint.
<br>- Select first a cloud storage provider to store the zarr file produced as output (AWS or Azure Blob Storage)
<br>- You can specify a value for the AWS S3 bucket where the file will be stored (default value can be set in env file: AWS_BUCKET_NAME).
<br>- Select then one or several indicator values to build the datacube in zarr format.
<br>- As example, you can then enter the following request body (polygon can be wkt or geojson)
<br>  
   Body Example for analytics_datacube_processor endpoint:
    (WKT)
   ```json
   {
   "polygon": "POLYGON((-90.41 41.6663, -90.41 41.6545, -90.3775 41.6541, -90.3778 41.6660, -90.41 41.6663))",
   "startDate": "2023-06-01",
   "endDate": "2023-07-01"
   }
   ```
   
   (GeoJson)
   ```json
   {
   "polygon": "{\"type\": \"Polygon\",\"coordinates\": [[[-90.41, 41.6663],[-90.41, 41.6545],[-90.3775, 41.6541],[-90.3778, 41.666],[-90.41, 41.6663]]]}",
   "startDate": "2023-06-01",
   "endDate": "2023-07-01"
   }
   ```

4. Closing the Docker container:

    To delete the container when it is not needed anymore run : 
    ```
    docker stop demo
    ```

<!-- PROJECT ORGANIZATION -->
## Project Organization

    ├── README.md          <- The top-level README for developers using this project.
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    ├── environment.yml    <- The conda requirements file for reproducing the analysis environment, e.g.
    │                         generated with `conda env export > environment.yml`, or manually
    │
    ├── pyproject.toml     <- Makes project pip installable (pip install -e .) so src can be imported
    ├── MANIFEST.in        <- Used to include/exclude files for package genration. 
    ├───src                <- Source code for use in tis project.
    │   ├───main.py 
    │   ├───api
    │   │   ├── files
    │   │   │   └── favicon.svg
    │   │   ├── __init__.py
    │   │   ├── constants.py
    │   │   └── api.py
    │   ├───data
    │   │   └── processor_input_example.json
    │   ├───data
    │   │   ├── __init__.py 
    │   │   ├── input_schema.py   
    │   │   └── output_schema.py
    │   ├───utils
    │   │   ├── __init__.py 
    │   │   └── file_utils.py
    │   └───analytics_datacube_processor
    │       ├── __init__.py
    │       ├── processor.py
    │       └── utils.py
    └── manifests
        ├── analytics-datacube.yml
        └── analytics-datacube-svc.yml

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- RESOURCES -->
## Resources 
The following links will provide access to more information:
- [EarthDaily agro developer portal  ](https://developer.geosys.com/)
- [Pypi package](https://pypi.org/project/geosyspy/)
- [Analytic processor template](https://github.com/earthdaily/Analytic-processor-template)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Support development

If this project has been useful, that it helped you or your business to save precious time, don't hesitate to give it a star.

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the [MIT License](https://github.com/earthdaily/Studies-and-Analysis/blob/main/LICENSE).

<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

For any additonal information, please [email us](mailto:sales@earthdailyagro.com).

<p align="right">(<a href="#top">back to top</a>)</p>

## Copyrights

© 2023 Geosys Holdings ULC, an Antarctica Capital portfolio company | All Rights Reserved.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
<!-- List of available shields https://shields.io/category/license -->
<!-- List of available shields https://simpleicons.org/ -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo.svg?style=social
[NETcore-shield]: https://img.shields.io/badge/.NET%20Core-6.0-green
[NETcore-url]: https://github.com/dotnet/core
[contributors-url]: https://github.com/github_username/repo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo.svg?style=plastic&logo=appveyor
[forks-url]: https://github.com/github_username/repo/network/members
[stars-shield]: https://img.shields.io/github/stars/analytics-datacube-processor/repo.svg?style=plastic&logo=appveyor
[stars-url]: https://github.com/github_username/repo/stargazers
[issues-shield]: https://img.shields.io/github/issues/earthdaily/analytics-datacube-processor/repo.svg?style=social
[issues-url]: https://github.com/earthdaily/analytics-datacube-processor/issues
[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: https://opensource.org/licenses/MIT
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=social&logo=linkedin
[linkedin-url]: https://www.linkedin.com/company/earthdailyagro/mycompany/
[twitter-shield]: https://img.shields.io/twitter/follow/EarthDailyAgro?style=social
[twitter-url]: https://img.shields.io/twitter/follow/EarthDailyAgro?style=social
[youtube-shield]: https://img.shields.io/youtube/channel/views/UCy4X-hM2xRK3oyC_xYKSG_g?style=social
[youtube-url]: https://img.shields.io/youtube/channel/views/UCy4X-hM2xRK3oyC_xYKSG_g?style=social
[language-python-shiedl]: https://img.shields.io/badge/python-3.9-green?logo=python
[language-python-url]: https://pypi.org/ 
[GitStars-shield]: https://img.shields.io/github/stars/earthdaily?style=social
[GitStars-url]: https://img.shields.io/github/stars/earthdaily?style=social
[CITest-shield]: https://img.shields.io/github/workflow/status/earthdaily/analytics-datacube-v2/Continous%20Integration
[CITest-url]: https://img.shields.io/github/workflow/status/earthdaily/analytics-datacube-v2/Continous%20Integration






