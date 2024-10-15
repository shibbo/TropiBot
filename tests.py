from data.feed import Feed, FeedManager
from data.outlook import Outlook
from data.wallet import Wallet
import time
import sys

BASINS = [ "at", "ep", "cp" ]
# if we are using local things, this is mainly for testing
USE_LOCAL = False

if __name__ == "__main__":
    mgr = FeedManager()

    # TWOs (Tropical Weather Outlooks)
    mgr.addFeed("AT_TWO", "https://www.nhc.noaa.gov/index-at.xml")
    mgr.addFeed("EP_TWO", "https://www.nhc.noaa.gov/index-ep.xml")
    mgr.addFeed("CP_TWO", "https://www.nhc.noaa.gov/index-cp.xml")

    if USE_LOCAL:
        wallet_url = "https://shibbo.net/trop/wallet_test.xml"
        discussion_url = "https://shibbo.net/trop/wallet_discussion_test.xml"
        mgr.addFeed("test", wallet_url)
        mgr.addFeed("test_disc", discussion_url)
    else:
        for basin in BASINS:
            for i in range(1, 5):
                wallet_url = f"https://www.nhc.noaa.gov/nhc_{basin}{i}.xml"
                discussion_url = f"https://www.nhc.noaa.gov/xml/TCD{basin.upper()}{i}.xml"
                feed_name = f"wallet_{basin}{i}"
                disc_name = f"disc_{basin.upper()}{i}"
                mgr.addFeed(feed_name, wallet_url)
                mgr.addFeed(disc_name, discussion_url)

    time.sleep(10)

    # store our current outlooks
    outlooks = {}
    outlooks["AT"] = Outlook(mgr.getFeedItems("AT_TWO"))
    outlooks["EP"] = Outlook(mgr.getFeedItems("EP_TWO"))
    outlooks["CP"] = Outlook(mgr.getFeedItems("CP_TWO"))

    wallets = {}

    if USE_LOCAL:
        wallets["test"] = Wallet(mgr.getFeedItems("test"), mgr.getFeedItems("test_disc"))
    else:
        for basin in BASINS:
            for i in range(1, 5):
                feed_name = f"wallet_{basin}{i}"
                disc_name = f"disc_{basin.upper()}{i}"       
                wallets[feed_name] = Wallet(mgr.getFeedItems(feed_name), mgr.getFeedItems(disc_name))

    mgr.stopAllFeeds()