import re
import shlex

SCRIPTING_RE = re.compile(r'(?<!\\)(?:(?:{{(.+?)}})|(?:<([^\s]+)>)|(?:(?<!{){(.+?)}))')
MAX_ITER_LENGTH = 10000


async def get_uvars(ctx):
    uvars = {}
    async for uvar in ctx.bot.mdb.uvars.find({"owner": ctx.message.author.id}):
        uvars[uvar['name']] = uvar['value']
    return uvars


async def set_uvar(ctx, name, value):
    await ctx.bot.mdb.uvars.update_one(
        {"owner": ctx.message.author.id, "name": name},
        {"$set": {"value": value}},
        True)


async def get_gvar_values(ctx):
    gvars = {}
    async for gvar in ctx.bot.mdb.gvars.find():
        gvars[gvar['key']] = gvar['value']
    return gvars


async def get_aliases(ctx):
    aliases = {}
    async for alias in ctx.bot.mdb.aliases.find({"owner": ctx.message.author.id}):
        aliases[alias['name']] = alias['commands']
    return aliases


async def get_servaliases(ctx):
    servaliases = {}
    async for servalias in ctx.bot.mdb.servaliases.find({"server": ctx.message.server.id}):
        servaliases[servalias['name']] = servalias['commands']
    return servaliases


async def get_snippets(ctx):
    snippets = {}
    async for snippet in ctx.bot.mdb.snippets.find({"owner": ctx.message.author.id}):
        snippets[snippet['name']] = snippet['snippet']
    return snippets


async def get_servsnippets(ctx):
    servsnippets = {}
    if ctx.message.server:
        async for servsnippet in ctx.bot.mdb.servsnippets.find({"server": ctx.message.server.id}):
            servsnippets[servsnippet['name']] = servsnippet['snippet']
    return servsnippets


async def parse_snippets(args: str, ctx) -> str:
    """
    Parses user and server snippets.
    :param args: The string to parse. Will be split automatically
    :param ctx: The Context.
    :return: The string, with snippets replaced.
    """
    tempargs = shlex.split(args)
    snippets = await get_servsnippets(ctx)
    snippets.update(await get_snippets(ctx))
    for index, arg in enumerate(tempargs):  # parse snippets
        snippet_value = snippets.get(arg)
        if snippet_value:
            tempargs[index] = snippet_value
        elif ' ' in arg:
            tempargs[index] = shlex.quote(arg)
    return " ".join(tempargs)