import discord
from discord.ext import commands
from discord.ui import Select, View, Button
from data.feed import FeedManager
from data.outlook import Outlook
from data.wallet import Wallet
import asyncio
import time

token = ""

# Load the token from a file
def load_token():
    with open("token.txt", "r") as f:
        return f.readline().strip()

BASINS = ["at", "ep", "cp"]
USE_LOCAL = False
outlooks = {}
wallets = {}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

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
    outlook_feeds = {
        "AT_TWO": "https://www.nhc.noaa.gov/index-at.xml",
        "EP_TWO": "https://www.nhc.noaa.gov/index-ep.xml",
        "CP_TWO": "https://www.nhc.noaa.gov/index-cp.xml"
    }

    for name, url in outlook_feeds.items():
        mgr.addFeed(name, url)

    time.sleep(5)
    
    outlooks["AT"] = Outlook(mgr.getFeedItems("AT_TWO"))
    outlooks["EP"] = Outlook(mgr.getFeedItems("EP_TWO"))
    outlooks["CP"] = Outlook(mgr.getFeedItems("CP_TWO"))

def initialize_wallets(mgr, use_local):
    if use_local:
        if mgr.hasFeed("test") and mgr.hasFeed("test_disc"):
            wallets["test"] = Wallet(mgr.getFeedItems("test"), mgr.getFeedItems("test_disc"))
        else:
            print("Warning: Test feeds do not exist. Skipping...")

    else:
        for basin in BASINS:
            for i in range(1, 6):
                wallet_name = f"wallet_{basin}{i}"
                disc_name = f"disc_{basin.upper()}{i}"

                if mgr.hasFeed(wallet_name) and mgr.hasFeed(disc_name):
                    cur_wallet = Wallet(mgr.getFeedItems(wallet_name), mgr.getFeedItems(disc_name))
                    
                    active_wallet_name = cur_wallet.stormName() if not cur_wallet.isInactive else wallet_name
                    wallets[active_wallet_name] = cur_wallet
                else:
                    print(f"Warning: Feeds '{wallet_name}' or '{disc_name}' do not exist. Skipping...")

async def periodic_wallet_update(mgr, interval=15):
    previous_advs_dates = {}

    while True:
        print("Polling update...")
        current_wallets = {name: wallet for name, wallet in wallets.items()}
        outlooks.clear()
        initialize_outlooks(mgr)
        wallets.clear()
        initialize_wallets(mgr, USE_LOCAL)
        
        for name, current_wallet in current_wallets.items():
            if current_wallet.isInactive:
                continue

            current_advs_date = current_wallet.getAdvsDate()

            print(f"Checking storm {name} with advisory date: {current_advs_date}")

            if name in previous_advs_dates:
                previous_advs_date = previous_advs_dates[name]

                if current_advs_date != previous_advs_date:
                    print(f"Advisory date changed for {name}: {previous_advs_date} -> {current_advs_date}")
                    channel = bot.get_channel(972638242836979742)
                    storm_view = StormView(current_wallet)
                    await channel.send(embed=storm_view.embed, view=storm_view)

            previous_advs_dates[name] = current_advs_date
        await asyncio.sleep(interval)

class StormView(View):
    def __init__(self, wallet):
        super().__init__()
        self.wallet = wallet
        self.current_page = 0

        # Create the buttons
        left_button = Button(label="◀️", style=discord.ButtonStyle.primary)
        right_button = Button(label="▶️", style=discord.ButtonStyle.primary)
        left_button.callback = self.left_button_callback
        right_button.callback = self.right_button_callback

        self.add_item(left_button)
        self.add_item(right_button)

        self.embed = self.create_embed()
    
    def create_embed(self):
        if self.current_page == 0:
            description = self.wallet.generateMainText()
            return discord.Embed(title="Advisory", description=description)
        elif self.current_page == 1:
            image_url = self.wallet.getStormCone()
            embed = discord.Embed(title="Storm Cone")
            embed.set_image(url=image_url)
            return embed
        elif self.current_page == 2:
            wind_probs_url = self.wallet.getStormWindProbs()
            embed = discord.Embed(title="Wind Probabilities")
            embed.set_image(url=wind_probs_url)
            return embed
        elif self.current_page == 3:
            return discord.Embed(title="TEMP 1", description="TEMP 1")
        elif self.current_page == 4:
            return discord.Embed(title="TEMP 2", description="TEMP 2")

    async def left_button_callback(self, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % 5
        await self.update_message(interaction)

    async def right_button_callback(self, interaction: discord.Interaction):
        self.current_page = (self.current_page + 1) % 5
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        self.embed = self.create_embed()
        await interaction.response.edit_message(embed=self.embed)

class TWOView(View):
    def __init__(self):
        super().__init__()
        self.options = ["AT", "EP", "CP"]
        self.current_index = 0

        left_button = Button(label="◀️", style=discord.ButtonStyle.primary)
        right_button = Button(label="▶️", style=discord.ButtonStyle.primary)

        left_button.callback = self.left_button_callback
        right_button.callback = self.right_button_callback

        self.add_item(left_button)
        self.add_item(right_button)

        self.embed = self.create_embed()
    
    def create_embed(self):
        current_outlook = self.options[self.current_index]
        description = f"Outlook for {current_outlook}:\n\n" + "\n".join(str(item) for item in outlooks[current_outlook].items)
        return discord.Embed(title=f"{current_outlook} Tropical Weather Outlook", description=description)

    async def left_button_callback(self, interaction: discord.Interaction):
        self.current_index = (self.current_index - 1) % len(self.options)
        await self.update_message(interaction)

    async def right_button_callback(self, interaction: discord.Interaction):
        self.current_index = (self.current_index + 1) % len(self.options)
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        self.embed = self.create_embed()
        await interaction.response.edit_message(embed=self.embed)

@bot.tree.command(name="storm", description="Displays a dropdown of active storms.")
async def storm(interaction: discord.Interaction):
    active_storms = [name for name, wallet in wallets.items() if not wallet.isInactive]
    
    select = Select(placeholder="Choose an active storm...", options=[
        discord.SelectOption(label=storm) for storm in active_storms
    ])

    async def select_callback(interaction: discord.Interaction):
        selected_storm = select.values[0]
        selected_wallet = wallets.get(selected_storm)

        if not selected_wallet:
            await interaction.response.send_message("No data available for the selected storm.", ephemeral=True)
            return
        
        view = StormView(selected_wallet)
        embed = view.create_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    select.callback = select_callback
    view = View()
    view.add_item(select)

    await interaction.response.send_message("Select a storm:", view=view, ephemeral=True)

@bot.tree.command(name="two", description="View the Tropical Weather Outlooks currently issued.")
async def two(interaction: discord.Interaction):
    view = TWOView()
    await interaction.response.send_message('Choose an option:', view=view, ephemeral=True)

@bot.tree.command(name="stormchannel", description="Sets the bot to update a channel's topic when storm data is polled.")
async def stormchannel(interaction: discord.Interaction, channel: discord.TextChannel, storm: str):
    await channel.edit(topic=storm)
    await interaction.response.send_message(f'The description for {channel.mention} has been updated to "{storm}".', ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

    mgr = FeedManager()

    add_feeds(mgr, USE_LOCAL)

    if not hasattr(bot, 'update_task'):
        bot.update_task = bot.loop.create_task(periodic_wallet_update(mgr))

    await bot.tree.sync()
    print("Bot is ready.")

if __name__ == "__main__":
    token = load_token()
    bot.run(token)
