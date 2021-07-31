import asyncio
import discord
from discord.ext import commands
import aiohttp
from requests_html import AsyncHTMLSession
import config
import nest_asyncio
import json

nest_asyncio.apply()

called = False
break_loop = False
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


bot.run(config.TOKEN, bot=True, reconnect=True)
