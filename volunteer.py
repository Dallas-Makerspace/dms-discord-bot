#!/usr/bin/python3
import logging as log
import discord, asyncio, argparse, sys

parser = argparse.ArgumentParser(description='Handle the #on_hand_volunteers channel.')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
                    const=True, default=False,
                    help='verbose output')
parser.add_argument('-q', '--quiet', dest='quiet', action='store_const',
                    const=True, default=False,
                    help='only output warnings and errors')
parser.add_argument('token', metavar='token', action='store',
                    help='discord auth token for the bot')
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
    log.debug('Logged in as')
    log.debug(client.user.name)
    log.debug(client.user.id)
    log.debug('------')

@client.event
async def on_message(message):
    if message.content == '!volunteer':
        log.debug('[%s] Role addition requested' % message.author)
        for author_role in message.author.roles:
            if author_role.name == 'volunteers':
                await client.send_message(message.channel, 'You already have that role')
                log.debug('[%s] Role already assigned' % message.author)
                break;
        else:
            for role in message.server.roles:
                if role.name == 'volunteers':
                    break
            else:
                await client.send_message(message.channel, 'An error has occured, the role does not exist')
                log.error("The volunteers role does not exist")

            await client.add_roles(message.author, role)
            await client.send_message(message.channel, 'Role added')
            log.info('[%s] Role added' % message.author)
    elif message.content == '!unvolunteer':
        log.debug('[%s] Role removal requested' % message.author)
        for author_role in message.author.roles:
            if author_role.name == 'volunteers':
                await client.remove_roles(message.author, author_role)
                await client.send_message(message.channel, 'Role removed')
                log.info('[%s] Role removed' % message.author)
                break;
        else:
            await client.send_message(message.channel, 'You did not have the role')
            log.debug('[%s] Role was already not assigned' % message.author)

client.run(args.token)
