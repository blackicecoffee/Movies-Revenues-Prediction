# Intro-DS-Project

## How to run
**On your project folder, following these steps:**

1. Create a virtual environment: `python -m venv <your_environment_name>`
2. Run virtual environment: `.\<your_environment_name>\Scripts\activate`
3. Install required libraries: `pip install -r requirements.txt`

Replace `<your_environment_name>` with your actual virtual environment name.

## Movies crawling system

**How to crawl more movies:**

```
cd crawler/
python movie_crawler.py --start_year <start_year> --end_year <end_year>
```

**Arguments:**

1. `--start_year`: The starting year that you want to start crawl movies (e.g 2020).
2. `--end_year`: The end year that you want to end crawl movies (e.g 2021).

***Notes:*** 
1. The `end_year` must be greater than or equal to `start_year`.
2. If no argument is specified, the system will only crawl movies from default year.
3. If only `start_year` is specified, the system will only crawl movies from this year.
4. If both `start_year` and `end_year` are specified, the system will crawl movies from year *start_year* to *end_year*.
