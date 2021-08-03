import asyncio
import discord
from discord.ext import commands
import aiohttp
from requests_html import AsyncHTMLSession
import config
import nest_asyncio
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API
from tweepy import Stream
import threading
import requests

nest_asyncio.apply()

twitter_id = "1407427126710747142"


class PodmanTweetStreamer(StreamListener):
    def on_data(self, tweet):
        parsed_data = json.loads(tweet)
        data = {
            "username": "Podman",
            "content": "@everyone",
            "allowed_mentions": {"parse": ["everyone"]},
            "author": {
                "name": "Podman",
                "icon_url": f"https://github.com/containers/podman/blob/main/logo/podman-logo.png",
            },
            "embeds": [
                {
                    "description": f"{parsed_data['text']}",
                    "title": "Announcement from Podman",
                    "footer": {"text": f"Posted at {parsed_data['created_at']}"},
                }
            ],
        }

        result = requests.post(config.WEBHOOK_URL, json=data)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            return False
        return super().on_error(status_code)


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.PREFIX),
    intents=discord.Intents.default(),
    help_command=None,
)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Podman"))
    print(f"Logged in as {bot.user.name}")
    return


@bot.command()
async def docs(ctx, *args):
    """[Renders the documentaion from docs.podman.io]

    Args:
        ctx : [context]
    """
    if len(args) == 0 or len(args) > 1:
        return await ctx.reply("`Invalid Arguments`")
    arg = args[0]
    query_url = (
        f"https://docs.podman.io/en/latest/search.html?q={arg}&check_keywords=yes"
    )
    try:
        session = AsyncHTMLSession()
        response = await session.get(query_url)
    except:
        return await ctx.send("`Failed to Establish Connection. Try again Later!`")
    else:
        await response.html.arender(sleep=2)
        await session.close()
        about = response.html.find(".search", first=True)
        a = about.find("li")
        pages = len(a)
        title, res = "", []
        print(a[0])

        if not pages:
            title = "`No Results Found`"
        else:
            title = f"`Results for: {arg}`"

        for i in range(pages):
            desc = f'[`{a[i].text}`]({str(list(a[i].find("a")[0].absolute_links)[0])})'
            embed = discord.Embed(title=title, description=desc, color=0xE8E3E3)
            res.append(embed)
        cur_page = 0
        reply_embed = await ctx.reply(embed=res[cur_page], mention_author=False)
        await reply_embed.add_reaction("◀️")
        await reply_embed.add_reaction("▶️")
        await reply_embed.add_reaction("\U0001F5D1")

        while True:
            try:
                reaction, user = await bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: user == ctx.author
                    and str(reaction.emoji) in ["◀️", "▶️", "\U0001F5D1"],
                    timeout=60,
                )
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    await reply_embed.edit(embed=res[cur_page])
                    await reply_embed.remove_reaction(reaction, ctx.author)

                elif str(reaction.emoji) == "◀️" and cur_page > 0:
                    cur_page -= 1
                    await reply_embed.edit(embed=res[cur_page])
                    await reply_embed.remove_reaction(reaction, ctx.author)

                elif str(reaction.emoji) == "\U0001F5D1":
                    await reply_embed.delete()
                else:
                    await reply_embed.remove_reaction(reaction, ctx.author)

            except asyncio.TimeoutError:
                await reply_embed.clear_reactions()


@bot.command()
async def inspect(ctx, *args):
    """[Fetch data from Docker Hub API, this is used to inspect the size of images]

    Args:
        ctx : [context]

    """
    name = args[0]
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://hub.docker.com/v2/repositories/library/{name}/tags"
        ) as response:
            if response.status != 200:
                return await ctx.reply("`Falied to fetch data | Try again later`")
            data = await response.text()
            json_data = json.loads(str(data))
            res = []
            for result in json_data["results"][:10]:
                res.append(
                    f"`{name}:{result['name']} => {round(result['full_size']/(1048576),2)} MB`"
                )
            res[0] += "•"
            embed = discord.Embed(
                title=f"`Results for {name}`",
                description="\n•".join(res),
                color=0xE8E3E3,
            )
            return await ctx.send(embed=embed)


# TODO: Do not hardcode the links
@bot.command()
async def links(ctx, *args):
    """[Render important links]

    Args:
        ctx, *args: [context and tuple arguments]
    """
    if len(args) == 1:
        if args[0] in ("tshoot", "trouble", "troubleshoot", "ts"):
            embed = discord.Embed(
                title="Troubleshooting Reference",
                description="https://github.com/containers/podman/blob/main/troubleshooting.md",
                color=0xE8E3E3,
            )
            return await ctx.send(embed=embed)
        elif args[0] in ("git", "github"):
            embed = discord.Embed(
                title="GitHub",
                description="https://github.com/containers/podman",
                color=0xE8E3E3,
            )
            return await ctx.send(embed=embed)
        elif args[0] in ("website", "webpage", "web"):
            embed = discord.Embed(
                title="Official Website",
                description="https://podman.io/",
                color=0xE8E3E3,
            )
            return await ctx.send(embed=embed)
        elif args[0] == "issues":
            embed = discord.Embed(
                title="GitHub Issues",
                description="https://github.com/containers/podman/issues",
                color=0xE8E3E3,
            )
            return await ctx.send(embed=embed)
        elif args[0] in ("prs", "PRS", "PRs", "PR", "pulls"):
            embed = discord.Embed(
                title="GitHub Pull Requests",
                description="https://github.com/containers/podman/pulls",
                color=0xE8E3E3,
            )
            return await ctx.send(embed=embed)
    else:
        return await ctx.reply("`Invalid Arguments`")


def establish_twitter_connection():
    global twitter_id

    listener = PodmanTweetStreamer()
    auth = OAuthHandler(config.API_TOKEN, config.API_TOKEN_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    stream = Stream(auth, listener)

    stream.filter(follow=[twitter_id])


if __name__ == "__main__":
    twitter_conn = threading.Thread(target=establish_twitter_connection)
    twitter_conn.start()
    bot.run(config.TOKEN, bot=True, reconnect=True)
