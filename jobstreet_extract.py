from datetime import datetime, timedelta
import re
from playwright.sync_api import sync_playwright


def scrape_jobstreet(job_keyword,location_keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://ph.jobstreet.com", timeout=60000)

        page.fill("input#keywords-input", job_keyword)
        page.keyboard.press("Enter") 
        page.locator("#SearchBar__Where").fill(location_keyword)
        page.click("button:has-text('SEEK')")
        
        
        try:
        
            page_counter = 1 
            jobs = []
            
            while True:
                page.wait_for_selector('[data-automation="normalJob"]', timeout=15000)
                job_elements = page.query_selector_all('[data-automation="normalJob"]')
            
                print(f"Page:{page_counter}")
                
                for index, job in enumerate(job_elements):
                    #test purposes limit the jobs for 2 counts per page
                    if index < 2:
                        counter = f"Clicking job {index + 1}/{len(job_elements)} : {page_counter}"
                        print(counter)
                        job.scroll_into_view_if_needed()        
                        job.click(force=True, position={"x": 50, "y": 1})
                        
                        page.wait_for_selector('h1', timeout=15000)
                        
                        #Extract information --- if those 2 variables will be commentd job description will not be extracted
                        job_title = page.text_content('[data-automation="job-detail-title"]') or "N/A"
                        company_name = page.text_content('[data-automation="advertiser-name"]') or "N/A"
                        location = page.text_content('[data-automation="job-detail-location"]') or "N/A"
                        industry = page.text_content('[data-automation="job-detail-classifications"]') or "N/A"
                        job_type = page.text_content('[data-automation="job-detail-work-type"]') or "N/A"
                        job_details = page.text_content('[data-automation="jobAdDetails"]') or "N/A" 
                        url_source = page.locator("h1.gepq850.eihuid4z").locator("a").get_attribute("href")
                        salary_element = page.query_selector('[data-automation="job-detail-add-expected-salary"]')
                        if not salary_element:
                            salary_element = page.query_selector('[data-automation="job-detail-salary"]')

                        salary = salary_element.text_content().strip() if salary_element else "N/A"
                        
                        date_searched = datetime.today()
                        date_text = page.locator("//span[contains(text(), 'Posted')]").inner_text()
                        
                        day_number = re.findall(r'\d+', date_text)  
                        days_to_add = int(day_number[0])
                        hour_or_day = date_text[-5]
                       
                        if  hour_or_day == 'd':
                            date_posted = date_searched - timedelta(days=days_to_add)
                        if  hour_or_day == "h":
                            date_posted = date_searched - timedelta(days=1)
                        if hour_or_day == "+":
                            date_posted = date_searched - timedelta(days=30)
                            
                        # job_description_element = page.query_selector('[data-automation="splitViewJobDetailsWrapper"]')
                        # job_description = job_description_element.text_content().strip() 
                        
                        job_overview = {"job title": job_title, 
                                            "company": company_name, 
                                            "location": location,
                                            "Industry": industry, 
                                            "date posted": job_type, 
                                            "expected salary": salary,
                                            "date_search": date_searched,
                                            "date_posted" : date_posted.date(),
                                            "url_source": url_source,
                                            "job details": job_details}
                                            
                        
                        jobs.append( job_overview)
                        page.wait_for_timeout(2000)
                    else:
                        break

                is_button_visible = page.is_visible( "a[title='Next']")
                next_button = page.locator("a[aria-label='Next']")
                print(is_button_visible)
                
                if is_button_visible == True and next_button.count() > 0 and len(job_elements) == 32:
                    print("Going to the next page...")
                    page.locator("a[aria-label='Next']").click()
                    page.wait_for_timeout(10000)  
                    page_counter += 1
                    
                else:
                    print("No more pages found. Exiting.")
                    break  
            
            browser.close()
            return jobs
        
        except Exception as e:
            print(f'Error in extracting data: {e}')
            
        finally:
            browser.close() 
            return jobs
        
        
scrape_jobstreet("data engineer", 'cavite')