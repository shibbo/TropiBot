import util.format

class Outlook:
    def __init__(self, items):
        # the info we want on this outlook is always going to be at index 0
        general_two = items[0]
        # remove all of the formatting data from the summary to make it look cleaner
        self.formattedText = util.format.clean_html(general_two['summary'])

    def getOutlookText(self):
        return self.formattedText