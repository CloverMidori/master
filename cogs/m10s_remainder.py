# -*- coding: utf-8 -*- #

from typing import Union
import discord
from discord.ext import commands, tasks
import datetime
import time

class m10s_remainder(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.remainder_check.start()

    @commands.group()
    async def remainder(self,ctx):
        pass

    @remainder.command()
    async def set(self,ctx,send_text,mention_at=None):
        if mention_at:
            try:
                mention_at = await commands.RoleConverter().convert(ctx,mention_at)
            except:
                mention_at = None
        rid = int(time.time())
        if mention_at:
            mention_at = mention_at.id
        await ctx.send("> リマインダー\n　日時を`2020/12/1 22:00`の形式で入力してください。")
        m = await self.bot.wait_for("message",check=lambda m:m.author.id == ctx.message.author.id)
        try:
            ts = datetime.datetime.strptime(m.content, "%Y/%m/%d %H:%M")
        except:
            await ctx.send("> リマインダー\n　日時の指定が誤っています。もう一度やり直してください。")
            return
        self.bot.cursor.execute("insert into remaind (id,stext,mention_role,time,chid) values (?,?,?,?,?)",(rid,send_text,mention_at,ts.timestamp(),ctx.channel.id))
        await ctx.send(f"> リマインダー\n　{ts.strftime('%Y/%m/%d %H:%M')}にリマインダーの登録をしました。(リマインダーID:`{rid}`)")

    @remainder.command()
    async def check(self,ctx,rid):
        self.bot.cursor.execute("select * from remaind where id = ?",(int(rid),))
        i = self.bot.cursor.fetchone()
        if i:
            e=discord.Embed(title="リマインド情報")
            try:
                e.add_field(name="メンションする役職のID",value=f"{i['mention_role'] or '(役職なし)'}")
            except:
                pass
            e.add_field(name="time",value=f"{datetime.datetime.fromtimestamp(i['time']).strftime('%Y/%m/%d %H:%M')}")
            e.add_field(name="テキスト",value=f"{i['stext']}")
            e.add_field(name="送信先チャンネル",value=f"<#{i['chid']}>")
            await ctx.send("> リマインダー\n　該当IDのリマインドが見つかりました！",embed=e)
        else:
            await ctx.send("> リマインダー\n　該当IDのリマインドは見つかりませんでした。")

    @remainder.command()
    async def delete(self,ctx,rid:int):
        self.bot.cursor.execute("delete from remaind where id = ?",(rid,))
        await ctx.send("> リマインダー\n　該当IDを持ったリマインドがある場合、それを削除しました。")


    @tasks.loop(minutes=1)
    async def remainder_check(self):
        now = datetime.datetime.now()
        self.bot.cursor.execute("select * from remaind")
        remainds = self.bot.cursor.fetchall()
        remaind_list = [i for i in remainds if datetime.datetime.fromtimestamp(i['time'])<= now]
        for i in remaind_list:
            ch = self.bot.get_channel(i["chid"])
            try:
                role = ch.guild.get_role(i["mention_role"])
            except:
                role = None
            try:
                await ch.send(f"> リマインド {role.mention if role else ''}\n　{i['stext']}")
            except:
                print("失敗したリマインダー")
            finally:
                self.bot.cursor.execute("delete from remaind where id = ?",(i["id"],))


def setup(bot):
    bot.add_cog(m10s_remainder(bot))