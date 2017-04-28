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

def get_channel(requested_channel):
    for channel in server.channels:
        if channel.name == requested_channel:
            return(channel)
    else:
        log.error("The #{0} channel does not exist".format(requested_channel))
        sys.exit(1)

def get_role(requested_role):
    for role in server.roles:
        if role.name == requested_role:
            return(role)
    else:
        log.error("The {0} role does not exist".format(requested_role))
        sys.exit(1)

def get_volunteers():
    volunteers = []
    for member in server.members:
        for member_role in member.roles:
            if member_role.name == "volunteers":
                volunteers.append(member)
                break
    return(volunteers)

@client.event
async def on_ready():
    global server
    global channels
    global roles

    log.info("Connected to discord")
    log.debug("Logged in as:")
    log.debug("User: {0}".format(client.user.name))
    log.debug("ID: {0}".format(client.user.id))

    # Hardcoded server ID for Dallas Makerspace
    server = client.get_server("300062029559889931")
    channels = dict()
    roles = dict()

    # Pre-load channels and roles so we don't have to look them up each time
    # Grab the info for the #on_hand_volunteers channel
    channels['on_hand_volunteers'] = get_channel("on_hand_volunteers")
    channels['infrastructure'] = get_channel("infrastructure")
    # Grab the info for the volunteers role
    roles['volunteers'] = get_role("volunteers")

@client.event
async def on_message(message):
    # Add user to the volunteers role
    if message.content == "!volunteer":
        log.debug("[{0}] Role addition requested".format(message.author))

        member = server.get_member_named(str(message.author))

        if not member:
            await client.send_message(message.author, "You are not a member of the Dallas Makerspace discord server")
            return

        # Check to see if the user already has this role
        for author_role in member.roles:
            if author_role.name == "volunteers":
                # They did, let them know they already had it
                msg = "{user} you already have access to the {channel} channel."
                await client.send_message(member, msg.format(user=member.mention, channel=channels['on_hand_volunteers'].mention))
                log.debug("[{0}] Role already assigned".format(member))
                break
        else:
            # They didn't have the role, so add it
            await client.add_roles(member, roles['volunteers'])
            log.info("[{0}] Role added".format(member))
            reply = "Hello {user}, you are now able to post in the {channel} channel. You can use `!unvolunteer` to be removed from the channel at anytime."
            await client.send_message(member, reply.format(user=member.mention, channel=channels['on_hand_volunteers'].mention))

            notification_msg = "{user} is now listed as an on hand volunteer and is available to help. There are currently {volunteers} volunteers available."
            await client.send_message(channels['on_hand_volunteers'], notification_msg.format(user=member.mention, volunteers=len(get_volunteers())))

    # Remove user from the volunteers role
    elif message.content == "!unvolunteer":
        log.debug("[{0}] Role removal requested".format(message.author))

        member = server.get_member_named(str(message.author))

        if not member:
            await client.send_message(message.author, "You are not a member of the Dallas Makerspace discord server")
            return

        # Check to see if the user has this role
        for author_role in member.roles:
            if author_role.name == "volunteers":
                # They did, so remove the role
                await client.remove_roles(member, author_role)
                log.info("[{0}] Role removed".format(member))
                msg = "Hello {user}, you have been removed from the {channel} channel, to re-join send `!volunteer` in any channel."
                await client.send_message(member, msg.format(user=member.mention, channel=channels['on_hand_volunteers'].mention))

                notification_msg = "{user} has left volunteer status. There are currently {volunteers} volunteers available."
                await client.send_message(channels['on_hand_volunteers'], notification_msg.format(user=member.mention, volunteers=len(get_volunteers())))
                break
        else:
            # They didn't have the role, do nothing
            msg = "{user}, you have already unsubscribed from the {channel} channel"
            await client.send_message(member, msg.format(user=member.mention, channel=channels['on_hand_volunteers'].mention))
            log.debug("[{0}] Role was already not assigned".format(member))

    # List the volunteers that are online
    elif message.content == "!volunteers":
        log.debug("[{0}] Requested information about volunteers".format(message.author))
        volunteers = get_volunteers()
        volunteers_msg = "There are currently {0} volunteers available.\n\n".format(len(volunteers))
        for volunteer in volunteers:
            volunteers_msg += ("@{0}\n".format(volunteer.name))
        await client.send_message(message.channel, volunteers_msg)

    # Request help from a volunteer
    elif message.content.startswith("!help"):
        log.debug("[{0}] Requested help from volunteers".format(message.author))

        if message.channel.is_private:
            request_method = "Private Message"
        else:
            request_method = message.channel.mention

        # Build the message for #on_hand_volunteers
        help_msg = "Eyes up, {volunteers}! {user} in {channel} needs help: {request}".format(
            volunteers=roles['volunteers'].mention,
            user=message.author.mention,
            channel=request_method,
            # Remove "!help " from the message
            request=message.content.split(' ', 1)[1]
        )
        await client.send_message(channels['on_hand_volunteers'], help_msg)

    # Show a help/about dialog
    elif message.content in ("!about", "!commands"):
        log.debug("[{0}] Requested information about us".format(message.author))
        msg = "I'm the friendly bot for managing various automatic rules and features of the Dallas Makerspace Discord chat server.\n\n" \
              "I understand the following commands:\n\n" \
              "`!about` or `!commands` - This about message.\n" \
              "`!help` - Request help from volunteers, for example `!help I can't access the fileserver` will send a request to the active volunteers.\n" \
              "`!volunteer` - Add yourself to the list of active volunteers, gain access to post in the {on_hand_volunteers} channel.\n" \
              "`!unvoluntter` - Remove yourself from the list of active volunteers and stop receiving notifcations.\n" \
              "`!volunteers` - List the active volunteers.\n" \
              "\nIf I'm not working correctly or you'd like to help improve me, please join the {infrastructure} channel.\n\n" \
              "My source code is available at: https://github.com/Dallas-Makerspace/dms-discord-bot." \
              .format(on_hand_volunteers=channels['on_hand_volunteers'].mention, infrastructure=channels['infrastructure'].mention)
        await client.send_message(message.channel, msg)
    elif message.content.startswith("!voluntell"):
        await client.send_message(message.channel, "{user} do it yourself".format(user=message.author.mention))

client.run(args.token)
