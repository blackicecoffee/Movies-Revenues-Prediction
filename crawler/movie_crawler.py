import requests
from bs4 import BeautifulSoup
import csv
import argparse

parser = argparse.ArgumentParser()

# Add argument
parser.add_argument("--start_year", type=int, default="2024")
parser.add_argument("--end_year", type=int)

args = parser.parse_args()
if args.end_year:
    if args.start_year > args.end_year and args.end_year:
        raise ValueError("End year must be greater than or equal to start year")


def writeCSV(movies: list, file_path: str) -> None:
    movies_fields = ['Title', 'Links',  'Distributor', 'Opening', 'Budget', 'Release Date',\
                  'MPAA', 'Running Time', 'Genres', 'In Release', 'Widest Release', \
                    'Director', 'Domestic', 'International', 'Worldwide']
    
    with open(file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(movies_fields)

        for movie in movies:
            row = [movie[0]['Title'], movie[0]['Links'], movie[0]['Distributor'], movie[0]['Opening'], movie[0]['Budget'] if len(movie[0]['Budget']) > 0 else "-", movie[0]['Release Date'],\
                    movie[0]['MPAA'], movie[0]['Running Time'], movie[0]['Genres'], movie[0]['In Release'], movie[0]['Widest Release'], movie[0]['Director'] if len(movie[0]['Director']) > 0 else "-",\
                        movie[0]['Domestic'], movie[0]['International'], movie[0]['Worldwide']]
            csv_writer.writerow(row)
        file.close()

def crawl_movies(starYear: int, endYear: int) -> None:
    base_url = "https://www.boxofficemojo.com"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    for year in range(starYear, endYear + 1):
        movies_lst = []
        main_url = base_url + '/year/' + str(year) + '/?grossesOption=calendarGrosses'
        main_response = requests.get(main_url, headers=headers)

        # Check if the request was successful
        if main_response.status_code == 200:
            print("--------------------------------")
            print(f"Successfully fetched the {main_url}!")
        else:
            print(f"Failed to retrieve the webpage. Status code: {main_response.status_code}")
            exit()

        # Parse the page
        main_soup = BeautifulSoup(main_response.content, 'html.parser')

        # Get all <tr> tags
        all_trs = main_soup.select("div.imdb-scroll-table-inner > table > tr")[1:] # Remove the first tr tag

        for tr_tag in all_trs:
            detail = [{
                'Title': '',
                'Links': '',
                'Distributor': '',
                'Opening': '',
                'Budget': '',
                'Release Date': '',
                'MPAA': '',
                'Running Time': '',
                'Genres': '',
                'In Release': '',
                'Widest Release': '',
                'Director': '',
                'Domestic': '',
                'International': '',
                'Worldwide': ''
            }]
            # <a> tag contain title and link
            title_a_tag = tr_tag.select("td.mojo-field-type-release > a")
            
            # Get title and link
            title = title_a_tag[0].text
            link = title_a_tag[0].get('href')

            detail[0]['Title'] = title
            detail[0]['Links'] = link

            # Process first child link
            child_url = base_url + link
            child_response = requests.get(child_url, headers=headers)

            if child_response.status_code == 200:
                print(f"\tCrawling movie: {title} from year: {year}")
            else:
                print(f"Failed to retrieve the webpage. Status code: {child_response.status_code}")
                exit()

            child_soup = BeautifulSoup(child_response.content, 'html.parser')

            performance_table = child_soup.select("div.mojo-performance-summary-table > div")
            summary_table = child_soup.select("div.mojo-summary-values > div")

            # Get gross
            for div in performance_table:
                performance_field_tag_name = div.select("span.a-size-small")[0]
                performance_field_tag_gross = div.select("span.a-size-medium")[0]

                performance_field_name = performance_field_tag_name.text
                performance_field_gross = performance_field_tag_gross.text

                if "Domestic" in performance_field_name:
                    detail[0]['Domestic'] = performance_field_gross
                elif 'International' in performance_field_name:
                    detail[0]['International'] = performance_field_gross
                elif 'Worldwide' in performance_field_name:
                    detail[0]['Worldwide'] = performance_field_gross
            
            # Get summary info
            for div in summary_table[::-1]:
                all_spans = div.select("span")
                    
                field_name = all_spans[0].text
                field_value = all_spans[1].text

                if field_name == 'Distributor':
                    link_text = ''
                    if len(all_spans[1].select("a")) > 0:
                        link_text = all_spans[1].select("a")[0].text
                        field_value = field_value.replace(link_text, '')

                if field_name == 'Opening':
                    field_value = all_spans[1].select("span")[0].text
                
                if field_name == 'Genres':
                    field_value = field_value.split('\n')
                    processed_field_value = []
                    for value in field_value:
                        value = value.strip()
                        if value != '':
                            processed_field_value.append(value.strip())
                    field_value = processed_field_value

                if "IMDbPro" in field_name: continue
                detail[0][field_name] = field_value
            
            # Get link to another info
            select_nav_link = child_soup.select("select#releasegroup-picker-navSelector")[0]
            option_links = select_nav_link.select("option")
            all_release_link = ''
            for option in option_links:
                option_text = option.text
                if option_text == "All Releases":
                    all_release_link = option.get('value')
                    break

            if len(all_release_link) > 0:
                all_release_url = base_url + all_release_link + "credits/?ref_=bo_tt_tab#tabs"
                all_release_response = requests.get(all_release_url, headers=headers)
                all_release_soup = BeautifulSoup(all_release_response.content, 'html.parser')
                all_release_summary_table = all_release_soup.select("div.mojo-summary-values > div")
                
                # Get budget if exist
                for div in all_release_summary_table:
                    all_spans = div.select("span")
                        
                    field_name = all_spans[0].text
                    field_value = all_spans[1].text

                    if field_name == "Budget":
                        detail[0]['Budget'] = field_value
                        break
            
                # Get director
                all_release_crew_table = all_release_soup.select("div.mojo-gutter > table#principalCrew > tr")
                for crew in all_release_crew_table[1:]:
                    crew_tds = crew.select("td")
                    crew_name = crew_tds[0].text
                    crew_role = crew_tds[1].text
                    if crew_role == "Director":
                        detail[0]['Director'] = crew_name
                        break

                all_release_response.close()
            child_response.close()   
            movies_lst.append(detail)
        main_response.close()
        print(f"Done crawling {main_url}")

        # Write to file
        csv_file = "../datasets/raw_data/" + str(year) + ".csv"
        print(f"Writing movies from {year} to {csv_file}")
        writeCSV(movies=movies_lst, file_path=csv_file)
        print(f"Done writing movies from {year} to {csv_file}.")

        print("--------------------------------")

startYear = args.start_year
endYear = args.end_year

if endYear == None:
    endYear = startYear

crawl_movies(starYear=startYear, endYear=endYear)