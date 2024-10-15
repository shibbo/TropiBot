import util.format

USE_LOCAL = True

class Wallet:
    def __init__(self, items, discussion_items):
        self.functions = {
            0: self.parseSummary,
            1: self.parsePublicAdvisory,
            2: self.parsePublicAdvisorySpa,
            3: self.parseForecastAdvisory,
            4: self.parseForecastDicussion,
            5: self.parseWindSpeedProbs,
            6: self.parseGraphics
        }

        # each wallet can contain a single storm. However, we can discard any wallets that have no current storm assigned to them.
        item = items[0]
        self.isInactive = "No current storm" in item['title']

        if self.isInactive:
            return

        self.items = items
        self.discussion_items = discussion_items
        self.headline = ""
        self.location = ""
        self.date = ""
        self.movement = ""
        self.windSpeed = ""
        self.name = ""
        self.pressure = ""
        self.advisory = ""
        self.advisoryLink = ""

        self.discussionHeader = ""
        self.discussionLink = ""
        self.discussionText = ""

        for i in range(6):
            self.functions[i]()
        pass

    def isInactive(self):
        return self.isInactive
    
    def parseSummary(self):
        # index 0 is our main summary
        item = self.items[0]
        self.advisoryLink = item['link']
        self.headline = item['nhc_headline']
        self.location = item['nhc_center']
        self.name = f"{item['nhc_type']} {item['nhc_name']}"
        self.date = item['nhc_datetime']
        self.movement = item['nhc_movement']
        self.pressure = item['nhc_pressure']
        self.windSpeed = item['nhc_wind']

    def parsePublicAdvisory(self):
        # index 1 is our public advisory
        item = self.items[1]
        self.advisory = item['title']

    def parsePublicAdvisorySpa(self):
        # we will implement this later
        pass

    def parseForecastAdvisory(self):
        pass

    def parseForecastDicussion(self):
        # index 4 is the forecast discussion
        item = self.items[4]
        self.discussionLink = item['link']
        self.discussionHeader = self.discussion_items[0]['title']
        self.discussionText = util.format.clean_html(self.discussion_items[0]['summary'])
        pass

    def parseWindSpeedProbs(self):
        pass

    def parseGraphics(self):
        pass