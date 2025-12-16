import os
import sys
import time
import requests

class RedditScraper:

    def __init__(self, folder:str, page_seed:str=None):
        self.folder = folder
        self.next_page_code = page_seed
        self.files_stored_counter = 0
        self.subreddit = None

    def set_subreddit(self, subreddit:str):
        self.subreddit = subreddit

    def get_base_url(self) -> str:
        if not self.subreddit:
            raise ValueError
        return f'https://www.reddit.com/r/{self.subreddit}.json'

    def get_query_params(self) -> dict:
        params = {
            "type": "link",
            "sort": "top",
            "limit": "100",
            "raw_json": "1",
            "include_over_18": "off"
        }
        if self.next_page_code:
            params['after'] = self.next_page_code
        return params

    def download_page_posts(self) -> list:
        posts_response = requests.get(self.get_base_url(), params=self.get_query_params(), headers={'User-Agent': 'automated script'})
        print(f'Fetched posts page from {posts_response.url}')
        if posts_response.status_code != 200:
            print(f'Response Data: {posts_response.text}')
        response_json = posts_response.json()
        # update next page pointer
        self.next_page_code = response_json['data']['after']
        # return a JSON document for each post on the page
        return response_json['data']['children']
    
    def image_already_stored(self, img_name:str) -> bool:
        filepath = f'{self.folder}/{self.subreddit}/{img_name}'
        if os.path.exists(filepath):
            print(f"File {filepath} already exists")
            return True
        return False

    def store_image(self, thumbnail_response):
        if not os.path.exists(f'{self.folder}/{self.subreddit}'):
            os.mkdir(f'{self.folder}/{self.subreddit}')

        thumbnail_img_name = thumbnail_response.url.split("/")[-1]
        filepath = f'{self.folder}/{self.subreddit}/{thumbnail_img_name}'

        if self.image_already_stored(thumbnail_img_name):
            return
        
        with open(filepath, 'wb') as fstream:
            fstream.write(thumbnail_response.content)
            self.files_stored_counter += 1

    def load_images(self):
        for i in range(10): # reddit wont let us load more than 1000 posts at a time, with a page size of 100, 10x100 = the absolute maximum
            print(f'Loading page {i+1} of {self.subreddit}')
            for post in self.download_page_posts():
                try:
                    thumbnail_url = post['data']['thumbnail']
                    # skip non .jpg files - reddit thumbnails are always jpg
                    if thumbnail_url.split(".")[-1] != 'jpg':
                        print(f'File type not supported: {thumbnail_url}')
                        continue

                    # dont try to download a file we already have
                    thumbnail_filename = thumbnail_url.split("/")[-1]
                    if scraper.image_already_stored(thumbnail_filename):
                        continue
                    
                    print(f'Requesting thumbnail URL: {thumbnail_url}')
                    thumbnail_response = requests.get(thumbnail_url, stream=True)
                    # write to images storage
                    self.store_image(thumbnail_response)
                    
                except Exception as e:
                    print(f'Exception: {e}')
                    print(f'Failed to load post: {post}')
                time.sleep(1) # we are scraping - be polite
            
            if not self.next_page_code:
                print("End of post book linked list found - terminating")
                break
            print("Sleeping so we dont upset Reddit API host")
            time.sleep(5)

if __name__ == '__main__':
    for subreddit in sys.argv[1].split(","): # allow specifying multiple subreddits eg `python3 scrape_subreddit.py pics,pictures,selfie,cats,dogs,food`
        scraper = RedditScraper('reddit')
        scraper.set_subreddit(subreddit)
        scraper.load_images()