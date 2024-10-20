import util.format

USE_LOCAL = True

class Wallet:
    def __init__(self, items, discussion_items):
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

        self.graphicsLinks = []

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

        # index 1 is our public advisory
        item = self.items[1]
        self.advisory = item['title']

        # after the two indicies, the format can change quite a bit
        # so we will use the element title to determine what we are looking at
        for i in range(2, len(self.items)):
            item = self.items[i]
            title = item['title']

            if "Spanish" in title:
                # todo -- parse spanish advisory
                pass
            elif "Forecast Advisory" in title:
                # todo -- parse forecast advisory
                pass
            elif "Forecast Discussion" in title:
                self.discussionLink = item['link']
                self.discussionHeader = self.discussion_items[0]['title']
                self.discussionText = util.format.clean_html(self.discussion_items[0]['summary'])
            elif "Wind Speed Probabilities" in title:
                pass
            elif f"{self.name} Graphics" in title:
                self.graphicsLinks = util.format.extract_png(item['description'])

    def isInactive(self):
        return self.isInactive
    
    def stormName(self):
        return self.items[0]['nhc_name']
    
    def parsePublicAdvisorySpa(self):
        # we will implement this later
        pass

    def parseForecastAdvisory(self):
        pass

    def parseWindSpeedProbs(self):
        pass

    def parseGraphics(self):
        item = self.items[6]
        pass

    # generates the description for the storm channel
    def generateDesc(self):
        return f"{self.date} | {self.location} | {self.movement} | MSW: {self.windSpeed} | {self.pressure} | insert picture here"
    
    def generateMainText(self):
        return f"""
        {self.name}
        {self.headline}
        As of {self.date}:
        Location: {self.location} moving {self.movement}
        Windspeed: {self.windSpeed}
        Pressure: {self.pressure}
        """

    def getStormCone(self):
        return self.graphicsLinks[0]
    
    def getStormWindProbs(self):
        return self.graphicsLinks[1]
    
    def getAdvsDate(self):
        return self.date