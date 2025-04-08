import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def find_job(job_keyword,location_keyword):
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
                    
                    if page_counter < 2 :  
                        
                        counter = f"Clicking job {index + 1}/{len(job_elements)} : {page_counter}"
                        print(counter)
                        job.scroll_into_view_if_needed()        
                        
                        job.click(force=True, position={"x": 50, "y": 1})
                        
                        page.wait_for_selector('h1', timeout=15000)
                         
                        #Extract the targeted css selector 
                        job_title = page.text_content('[data-automation="job-detail-title"]') or "N/A"
                        company_name = page.text_content('[data-automation="advertiser-name"]') or "N/A"
                        location = page.text_content('[data-automation="job-detail-location"]') or "N/A"
                        industry = page.text_content('[data-automation="job-detail-classifications"]') or "N/A"
                        job_type = page.text_content('[data-automation="job-detail-work-type"]') or "N/A"
                        job_details = page.text_content('[data-automation="jobAdDetails"]') or "N/A" 
                        url_source = page.text_content('[data-automation="job-detail-title"]') or "N/A"  
                        # page.locator("h1.gepq850.eihuid4z").locator("a").get_attribute("href")
                        
                        salary_element = page.query_selector('[data-automation="job-detail-add-expected-salary"]')
                        
                        # redefinition of salary element if missing:
                        if not salary_element:
                            salary_element = page.query_selector('[data-automation="job-detail-salary"]')
                            
                        salary = salary_element.text_content().strip() if salary_element else "N/A"
                        
                        date_searched = datetime.today()
                        date_text = page.locator("//span[contains(text(), 'Posted')]").inner_text()
                        day_number = re.findall(r'\d+', date_text)  
                        day_number = int(day_number[0])
                        unit = date_text[-5]

                        date_posted = date_searched - timedelta(days=day_number) if unit == 'd' else \
                                      date_searched - timedelta(days=1) if unit == 'h' else \
                                      date_searched - timedelta(days=30)
                        
                        job_overview = {"job title": job_title, 
                                            "company": company_name, 
                                            "location": location,
                                            "Industry": industry, 
                                            "job_type": job_type, 
                                            "expected salary": salary,
                                            "date_search": date_searched.strftime("%Y-%m-%d"),
                                            "date_posted" : date_posted.strftime("%Y-%m-%d"),
                                            "url_source": url_source,
                                            "job_details": job_details}
                                            
                        jobs.append( job_overview)
                        page.wait_for_timeout(2000)
                    else: 
                        break
  
                next_button = page.locator("a[aria-label='Next']")

                if  next_button.count() > 0 and len(job_elements) == 32:
                    print("Going to the next page...")
                    page.locator("a[aria-label='Next']").click()
                    page.wait_for_timeout(10000)  
                    page_counter += 1
                    
                else:
                    print("No more pages found. Exiting.")
                    break  
            
            return jobs
        
        except Exception as e:
            print(f'Error in extracting data: {e}')
            return jobs
        
        finally:
            browser.close() 
            
        
        