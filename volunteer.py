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

def get_volunteers(members):
    volunteers = []
    for member in members:
        for member_role in member.roles:
            if member_role.name == "volunteers":
                volunteers.append(member)
                break
    return(volunteers)

def count_volunteers(members):
    count = 0
    for member in members:
        for member_role in member.roles:
            if member_role.name == "volunteers":
                count += 1
                break
    return(count)

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
            log.info("[{0}] Role added".format(message.author))
            reply = "Hello {user}, you are now able to post in the {channel} channel. You can use `!unvolunteer` to be removed from the channel at anytime."
            await client.send_message(message.channel, reply.format(user=message.author.mention, channel=on_hand_volunteers.mention))

            volunteers = count_volunteers(message.server.members)
            notification_msg = "{user} is now listed as an on hand volunteer and is available to help. There are currently {volunteers} volunteers available."
            await client.send_message(on_hand_volunteers, notification_msg.format(user=message.author.mention, volunteers=volunteers))

    # Remove user from the volunteers role
    elif message.content == "!unvolunteer":
        # Grab the info for the #on_hand_volunteers channel
        on_hand_volunteers = get_channel(message, "on_hand_volunteers")
        if not on_hand_volunteers:
            # Channel doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the #on_hand_volunteers channel does not exist. Please tell @nerds something is wrong!")
            return

        log.debug("[{0}] Role removal requested".format(message.author))

        # Check to see if the user has this role
        for author_role in message.author.roles:
            if author_role.name == "volunteers":
                # They did, so remove the role
                await client.remove_roles(message.author, author_role)
                log.info("[{0}] Role removed".format(message.author))
                msg = "Hello {user}, you have been removed from the {channel} channel, to re-join send `!volunteer` in any channel."
                await client.send_message(message.channel, msg.format(user=message.author.mention, channel=on_hand_volunteers.mention))

                volunteers = count_volunteers(message.server.members)
                notification_msg = "{user} has left volunteer status. There are currently {volunteers} volunteers available."
                await client.send_message(on_hand_volunteers, notification_msg.format(user=message.author.mention, volunteers=volunteers))
                break
        else:
            # They didn't have the role, do nothing
            msg = "{user}, you have already unsubscribed from the {channel} channel"
            await client.send_message(message.channel, msg.format(user=message.author.mention, channel=on_hand_volunteers.mention))
            log.debug("[{0}] Role was already not assigned".format(message.author))

    # List the volunteers that are online
    elif message.content == "!volunteers":
        log.debug("[{0}] Requested information about volunteers".format(message.author))
        volunteers = get_volunteers(message.server.members)
        volunteers_msg = "There are currently {0} volunteers available.\n\n".format(len(volunteers))
        for volunteer in volunteers:
            volunteers_msg += ("@{0}\n".format(volunteer.name))
        await client.send_message(message.channel, volunteers_msg)

    # Request help from a volunteer
    elif message.content.startswith("!help"):
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

        log.debug("[{0}] Requested help from volunteers".format(message.author))

        # Remove "!help " from the message
        request = message.content.split(' ', 1)[1]

        # Build the message for #on_hand_volunteers
        help_msg = "Eyes up, {volunteers}! {user} in {channel} needs help: {request}".format(
            volunteers=volunteers_role.mention,
            user=message.author.mention,
            channel=message.channel.mention,
            request=request
        )
        await client.send_message(on_hand_volunteers, help_msg)

    # Show a help/about dialog
    elif message.content in ("!about", "!commands"):
        # Grab the info for the #on_hand_volunteers channel
        on_hand_volunteers = get_channel(message, "on_hand_volunteers")
        if not on_hand_volunteers:
            # Channel doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the #on_hand_volunteers channel does not exist. Please tell @nerds something is wrong!")
            return
        # Grab the info for the #infrastructure channel
        infrastructure = get_channel(message, "infrastructure")
        if not infrastructure:
            # Channel doesn't exist, something is wrong!
            await client.send_message(message.channel, "An error has occured, the #infrastructure channel does not exist. Please tell @nerds something is wrong!")
            return

        log.debug("[{0}] Requested information about us".format(message.author))
        msg = "I'm the friendly bot for managing various automatic rules and features of the Dallas Makerspace Discord chat server.\n\n" \
              "I understand the following commands:\n\n" \
              "`!about` or `!commands` - This about message.\n" \
              "`!help` - Request help from volunteers, for example `!help I can't access the fileserver` will send a request to the active volunteers.\n" \
              "`!volunteer` - Add yourself to the list of active volunteers, gain access to post in the {on_hand_volunteers} channel.\n" \
              "`!unvoluntter` - Remove yourself from the list of active volunteers once you are done for the day.\n" \
              "`!volunteers` - List the active volunteers.\n" \
              "\nIf I'm not working correctly or you'd like to help improve me, please join the {infrastructure} channel.\n\n" \
              "My source code is available at: https://github.com/Dallas-Makerspace/dms-discord-bot." \
              .format(on_hand_volunteers=on_hand_volunteers.mention, infrastructure=infrastructure.mention)
        await client.send_message(message.channel, msg)
    elif message.content.startswith("!voluntell"):
        await client.send_message(message.channel, "{user} do it yourself".format(user=message.author.mention))

client.run(args.token)
