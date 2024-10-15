from data.feed import Feed, FeedManager
import time
import sys

if __name__ == "__main__":
    mgr = FeedManager()

    mgr.addFeed("ATL", "https://www.nhc.noaa.gov/xml/TWDAT.xml")
    mgr.addFeed("EPAC", "https://www.nhc.noaa.gov/xml/TWDEP.xml")

    time.sleep(10)

    atl_items = mgr.getFeedItems("ATL")
    epac_items = mgr.getFeedItems("EPAC")

    # expecting the length to be 1 for each
    print(f"ATL Feed: {len(atl_items)}")
    print(f"EPAC Feed: {len(epac_items)}")

    mgr.stopAllFeeds()