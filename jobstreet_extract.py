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
        
        page_counter = 1 
        jobs = []

        while True:
            page.wait_for_selector('[data-automation="normalJob"]', timeout=15000)
            job_elements = page.query_selector_all('[data-automation="normalJob"]')
        
            print(f"Page:{page_counter}")
            
            for index, job in enumerate(job_elements):
                #test purposes limit the jobs for 2 counts
                if index < 2:
                    print(f"Clicking job {index + 1}/{len(job_elements)} : {page_counter}")
                    job.scroll_into_view_if_needed()        
                    job.click(force=True, position={"x": 50, "y": 1})
                    
                    page.wait_for_selector('h1', timeout=15000)
                    
                    #Extract information --- if those 2 variables will be commentd job description will not be extracted
                    job_title = page.text_content('h1') or "N/A"
                    company_name = page.text_content('[data-automation="advertiser-name"]') or "N/A"
                    # location = page.text_content('[data-automation="job-detail-location"]') or "N/A"
                    # job_type = page.text_content('[data-automation="job-detail-classifications"]') or "N/A"
                    # posted_time = page.text_content('[data-automation="job-detail-work-type"]') or "N/A"
                    # salary_element = page.query_selector('[data-automation="job-detail-add-expected-salary"]')
                    # if not salary_element:
                    #     salary_element = page.query_selector('[data-automation="job-detail-salary"]')

                    # salary = salary_element.text_content().strip() if salary_element else "N/A"
                    
                    job_description_element = page.query_selector('[data-automation="splitViewJobDetailsWrapper"]')
                    job_description = job_description_element.text_content().strip() 
                    
                    print(job_description)
                    jobs.append(job_description)
                    page.wait_for_timeout(2000)
                else:
                    break

            next_button = page.locator("a[aria-label='Next']")
            
            if next_button.count() > 0:
                print("Going to the next page...")
                next_button.click()
                page.wait_for_timeout(10000)  
                page_counter += 1
                
            else:
                print("No more pages found. Exiting.")
                break  
        
        browser.close()
        return jobs
