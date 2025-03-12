from playwright.sync_api import sync_playwright, Playwright
from playwright_stealth import stealth

jobstreet_url = r'https://ph.jobstreet.com'
indeed_url = r'https://ph.indeed.com/?r=us'

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/134.0'

with sync_playwright() as p:
    
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(user_agent=user_agent)
    page = context.new_page()
    
    page.goto(jobstreet_url)
    
    page.fill("input#keywords-input", "data engineer")
    page.fill("input#SearchBar__Where", "Laguna Calabarzon")
    page.click("button:has-text('SEEK')")
    page.wait_for_selector('[data-automation="normalJob"]', timeout=15000)
        


    next_button = page.locator("span:has-text('Next')")

   
    #jobcard-1 > div.gepq850.eihuid5j.eihuid0._1qnq8v60
    #jobcard-2 > div.gepq850.eihuid5j.eihuid0._1qnq8v60
    
    # elements = page.query_selector_all("[data-automation='job-list-view-job-link']")
    # print(len(elements))
    # counter = 0

    # for element in elements:
    #     print(element.text_content())
    #     counter =+ 1
    #     print(counter)
        
    # job_links = page.query_selector_all("[data-automation='job-list-view-job-link']")
    # print(len(job_links))

    # for link in job_links:
    #     print(link.get_attribute("href")) 

    # job_links = page.locator("div.gepq850.eihuid4z.eihuid4x a[data-automation='job-list-view-job-link']").all()
        
    # # Extract href values into a list
    # job_urls = [link.get_by_text() for link in job_links]
    # print(job_links)
    # elements = page.locator("div.gepq850 a").all
    
    # # for element in elements:
    # #     element.click()    
    # page.wait_for_selector('[data-automation="job-list-view-job-link"]')

    # jobs = page.locator('[data-automation="job-list-item-link-overlay"]').click()
    # # counter = 0

    # # for job in jobs:
    # #     job.get_attribute("data-automation")
    # #     counter += 1
    # #     print(counter)
        
        
    # job_count = [job_card.get_attribute('id') for job_card in job_cards]
        
    # job_elements = page.locator("[data-automation='job-list-view-job-link']").all()
    
    # #jobcard-1 > div.gepq850.eihuid4v.eihuid51 > a
    
    # for job in job_elements:
    #     job.click()
    #     text = job.all_inner_texts()  # Get the inner text
    #     print(text)  # Print the job title or relevant details
        
    #     # Click the job to open details if required
        
    #     page.wait_for_timeout(2000)  # Wait for details to load if necessary

        
    # '''--------------------------------------------------------------------------------'''
    # links = page.locator("div.gepq850 a").all()

    # # Extract href attributes
    # hrefs = [link.get_attribute("href") for link in links]
    # count = 0
    
    # # Print results
    # for href in hrefs:
    #     print(f'ph.jobstreet.com/{href}')
    #     count += 1
        
    # print(count)

    page.wait_for_timeout(15000)
    
    
 
    
    