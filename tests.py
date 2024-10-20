from data.feed import FeedManager
from data.outlook import Outlook
from data.wallet import Wallet
import time

BASINS = ["at", "ep", "cp"]
USE_LOCAL = False  # Toggle this to switch between local and remote URLs

def add_feeds(mgr, use_local):
    if use_local:
        add_local_feeds(mgr)
    else:
        add_remote_feeds(mgr)

def add_local_feeds(mgr):
    wallet_url = "https://shibbo.net/trop/wallet_test.xml"
    discussion_url = "https://shibbo.net/trop/wallet_discussion_test.xml"
    mgr.addFeed("test", wallet_url)
    mgr.addFeed("test_disc", discussion_url)
    print("Added local test feeds.")

def add_remote_feeds(mgr):
    for basin in BASINS:
        for i in range(1, 6):
            wallet_url = f"https://www.nhc.noaa.gov/nhc_{basin}{i}.xml"
            discussion_url = f"https://www.nhc.noaa.gov/xml/TCD{basin.upper()}{i}.xml"
            mgr.addFeed(f"wallet_{basin}{i}", wallet_url)
            mgr.addFeed(f"disc_{basin.upper()}{i}", discussion_url)
    print("Added remote feeds for all basins.")

def initialize_outlooks(mgr):
    mgr.addFeed("AT_TWO", "https://www.nhc.noaa.gov/index-at.xml")
    mgr.addFeed("EP_TWO", "https://www.nhc.noaa.gov/index-ep.xml")
    mgr.addFeed("CP_TWO", "https://www.nhc.noaa.gov/index-cp.xml")

    time.sleep(5)

    outlooks = {
        "AT": Outlook(mgr.getFeedItems("AT_TWO")),
        "EP": Outlook(mgr.getFeedItems("EP_TWO")),
        "CP": Outlook(mgr.getFeedItems("CP_TWO")),
    }
    print("Outlooks initialized.")
    return outlooks

def initialize_wallets(mgr, use_local):
    wallets = {}
    if use_local:
        wallets["test"] = Wallet(mgr.getFeedItems("test"), mgr.getFeedItems("test_disc"))
    else:
        for basin in BASINS:
            for i in range(1, 6):
                wallet_name = f"wallet_{basin}{i}"
                disc_name = f"disc_{basin.upper()}{i}"
                cur_wallet = Wallet(mgr.getFeedItems(wallet_name), mgr.getFeedItems(disc_name))
                active_wallet_name = cur_wallet.stormName() if not cur_wallet.isInactive else wallet_name
                wallets[active_wallet_name] = cur_wallet

    print("Wallets initialized.")
    return wallets

if __name__ == "__main__":
    mgr = FeedManager()

    add_feeds(mgr, USE_LOCAL)
    
    time.sleep(10)

    outlooks = initialize_outlooks(mgr)
    wallets = initialize_wallets(mgr, USE_LOCAL)

    mgr.stopAllFeeds()
    print("Feeds stopped. Test complete.")