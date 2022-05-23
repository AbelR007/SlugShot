# Help Commands
# class MyHelp(commands.HelpCommand):
#     def get_command_signature(self, command):
#         return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)
#
#     # colour_id =
#     async def send_bot_help(self, mapping):
#         embed = discord.Embed(title="SlugShot", colour=bot.main)
#         for cog, commands in mapping.items():
#             # filtered = await self.filter_commands(commands, sort=True)
#             command_signatures = [
#                 self.get_command_signature(c) for c in commands
#             ]
#             # print(command_signatures)
#             if command_signatures:
#                 cog_name = getattr(cog, "qualified_name", "No Category")
#                 if cog_name == "No Category":
#                     continue
#                 embed.add_field(name=cog_name, value="\n".join(
#                     command_signatures), inline=True)
#
#         channel = self.get_destination()
#         embed.set_footer(text="< > Required  |  [ ] Optional ")
#         await channel.send(embed=embed)
#
#     async def send_command_help(self, command):
#         embed = discord.Embed(title=self.get_command_signature(command), color=bot.main)
#         if command.description is None:
#             command.description = 'None'
#         embed.add_field(name="Description :", value=command.description)
#         alias = command.aliases
#         if alias:
#             embed.add_field(
#                 name="Aliases :", value=", ".join(alias), inline=False)
#
#         channel = self.get_destination()
#         embed.set_footer(text="< > Required  |  [ ] Optional ")
#         await channel.send(embed=embed)
#================
