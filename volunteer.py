#!/usr/bin/python3
import logging as log
import discord, asyncio, argparse, sys

parser = argparse.ArgumentParser(description="Handle the #on_hand_volunteers channel.")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_const",
                    const=True, default=False,
                    help="verbose output")
parser.add_argument("-q", "--quiet", dest="quiet", action="store_const",
                    const=True, default=False,
                    help="only output warnings and errors")
parser.add_argument("token", metavar="token", action="store",
                    help="discord auth token for the bot")
args = parser.parse_args()

if args.verbose:
    log.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=log.DEBUG, stream=sys.stdout)
    log.debug("Verbose output enabled")
elif args.quiet:
    log.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=log.WARNING, stream=sys.stdout)
else:
    log.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=log.INFO, stream=sys.stdout)

log.info("Started")

client = discord.Client()

@client.event
async def on_ready():
    log.info("Connected to discord")
    log.debug("Logged in as:")
    log.debug("User: {0}".format(client.user.name))
    log.debug("ID: {0}".format(client.user.id))

def get_channel(message, requested_channel):
    for channel in message.server.channels:
        if channel.name == requested_channel:
            return(channel)
    else:
        log.error("The #{0} channel does not exist".format(requested_channel))
        return(false)

def get_role(message, requested_role):
    for role in message.server.roles:
        if role.name == requested_role:
            return(role)
    else:
        log.error("The {0} role does not exist".format(requested_role))
        return(false)

@client.event
async def on_message(message):
    # Add user to the volunteers role
    if message.content == "!volunteer":
        # Grab the info for the #on_hand_volunteers channel
        on_hand_volunteers = get_channel(message, "on_hand_volunteers")
        if not on_hand_volunteers:
            # Channel doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the #on_hand_volunteers channel does not exist. Please tell @nerds something is wrong!")
            return

        # Grab the info for the volunteers role
        volunteers_role = get_role(message, "volunteers")
        if not volunteers_role:
            # Role doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the volunteers role does not exist. Please tell @nerds something is wrong!")
            return

        log.debug("[{0}] Role addition requested".format(message.author))

        # Check to see if the user already has this role
        for author_role in message.author.roles:
            if author_role.name == "volunteers":
                # They did, let them know they already had it
                msg = "{user} you already have access to the {channel} channel."
                await client.send_message(message.channel, msg.format(user=message.author.mention, channel=on_hand_volunteers.mention))
                log.debug("[{0}] Role already assigned".format(message.author))
                break
        else:
            # They didn't have the role, so add it
            await client.add_roles(message.author, volunteers_role)
            msg = "Hello {user}, you are now able to post in the {channel} channel. You can use `!unvolunteer` to be removed from the channel at anytime."
            await client.send_message(message.channel, msg.format(user=message.author.mention, channel=on_hand_volunteers.mention))
            log.info("[{0}] Role added".format(message.author))

    # Remove user from the volunteers role
    elif message.content == "!unvolunteer":
        # Grab the info for the #on_hand_volunteers channel
        on_hand_volunteers = get_channel(message, "on_hand_volunteers")
        if not on_hand_volunteers:
            # Channel doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the #on_hand_volunteers channel does not exist. Please tell @nerds something is wrong!")
            return

        # Grab the info for the volunteers role
        on_hand_volunteers = get_channel(message, "on_hand_volunteers")
        if not on_hand_volunteers:
            await client.send_message(message.channel, "An error has occured, the #on_hand_volunteers channel does not exist. Please tell @nerds something is wrong!")
            return

        log.debug("[{0}] Role removal requested".format(message.author))

        # Check to see if the user has this role
        for author_role in message.author.roles:
            if author_role.name == "volunteers":
                # They did, so remove the role
                await client.remove_roles(message.author, author_role)
                msg = "Hello {user}, you have been removed from the {channel} channel, to re-join send `!volunteer` in any channel."
                await client.send_message(message.channel, msg.format(user=message.author.mention, channel=on_hand_volunteers.mention))
                log.info("[{0}] Role removed".format(message.author))
                break
        else:
            # They didn't have the role, do nothing
            msg = "{user}, you have already unsubscribed from the {channel} channel"
            await client.send_message(message.channel, msg.format(user=message.author.mention, channel=on_hand_volunteers.mention))
            log.debug("[{0}] Role was already not assigned".format(message.author))

    # Show a help/about dialog
    elif message.content in ("!about", "!help"):
        # Grab the info for the #infrastructure channel
        infrastructure = get_channel(message, "infrastructure")
        if not infrastructure:
            # Channel doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the #infrastructure channel does not exist. Please tell @nerds something is wrong!")
            return

        log.debug("[{0}] Requested information about us".format(message.author))
        msg = "I'm the friendly bot for managing various automatic rules and features of the Dallas Makerspace Discord chat server.\n\n" \
              "If I'm not working correctly or you'd like to help improve me, please join the {0} channel.\n\n" \
              "My source code is available at: https://github.com/Dallas-Makerspace/dms-discord-bot.".format(infrastructure.mention)
        await client.send_message(message.channel, msg)

client.run(args.token)
