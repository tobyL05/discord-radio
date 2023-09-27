import json
import os
import asyncio
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(">"),description="Radio bot",intents = intents)

@bot.command()
async def h(ctx):
	helpEmbed = discord.Embed(title="Commands")
	helpEmbed.add_field(name=">play *radio id*",value="Plays the requested radio stations (check >stations for available stations)",inline=False)
	helpEmbed.add_field(name=">stop",value="Stops playing the current radio station and disconnects",inline=False)
	helpEmbed.add_field(name=">stations",value="Lists available radio stations and their radio id",inline=False)
	await ctx.send(embed=helpEmbed)

class Radio(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		radioids = open("radioid.json")
		self.radioids = json.load(radioids)
		radioids.close()

		stations = open("stations.json")
		self.stations = json.load(stations)
		stations.close()

		self.ffmpegPath = "ffmpeg\\bin\\ffmpeg.exe"
		self.ffmpegOptions =  {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
		self.currstation = None

	@commands.command()
	async def play(self,ctx):
		"""join a voice channel and start playing requested radio station"""
		radioid = str(ctx.message.content).split()[1]
		#print("play")
		if radioid in self.radioids.keys(): #validate
			if radioid != self.currstation:
				self.currstation = radioid
				voice = ctx.voice_client
				if voice.is_playing():
					voice.stop()

				voice.play(discord.FFmpegPCMAudio(source=self.stations[radioid],options=self.ffmpegOptions,executable=self.ffmpegPath))
				#print(f"playing {self.radioids[radioid]}")
				await ctx.send(f"Playing {self.radioids[radioid]}")
			else:
				await ctx.send(f"Already playing {self.radioids[radioid]}!")
		else:
				#print("unknown radio id")
				await ctx.send(f"Unknown radio id: {self.radioids[radioid]}")


	@commands.command()
	async def stop(self,ctx):
		"""check_voice then dc bot"""
		#print("disconnecting")
		self.currstation = None
		await ctx.voice_client.disconnect()

	@commands.command()
	async def stations(self,ctx):
		"""show available radio stations"""
		f = open("stations.json")
		urls = json.load(f)
		f.close()
		stationsEmbed = discord.Embed(title="Available stations")
		for key in urls.keys():
			id = key.lower().replace(" ","")
			stationsEmbed.add_field(name=key,value=f"type: >play {id}",inline="false")
		await ctx.send(embed=stationsEmbed)

	@play.before_invoke
	@stop.before_invoke
	async def check_voice(self,ctx):
		#print("check_voice")
		"""check if author is in a voice channel"""
		
		"""if no voice_client or there is voice client but diff voice channel"""
		if ctx.voice_client is None:
			if ctx.author.voice: #if message author in vc
				await ctx.author.voice.channel.connect() #connect the bot
			else:
				await ctx.send("Connect to a voice channel!") #message author not in the channel
		elif ctx.voice_client.is_playing(): #if bot is currently playing something, stop. (for stop command)
			if len(str(ctx.message.content).split()) > 1: #there is message content so switch radio stations
				#switch radio stations
				pass
			else:
				ctx.voice_client.stop()	

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to discord")

async def main():
	async with bot:
		#with open("token.txt","r") as f:
			#token = f.readline()
		
		await bot.add_cog(Radio(bot))
		await bot.start(os.environ.get("BOT_KEY"))

if __name__ == "__main__":
	asyncio.run(main())
