import unittest
from scraper import scrape_job_listings

class TestScraper(unittest.TestCase):
    def test_scrape_job_listings(self):
        url = "https://careers.google.com/jobs/results/"
        listings = scrape_job_listings(url)
        self.assertIsInstance(listings, list)
        self.assertTrue(len(listings) > 0)

if __name__ == '__main__':
    unittest.main()