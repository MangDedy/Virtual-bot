import io
import sys
import os
import traceback
import asyncio
import time
import json
import requests
from pyrogram import Client, filters
from subprocess import run as srun

own = [1928677026,2003696861]

app = Client(
    'my_account',
    api_id=18079109,
    api_hash="61150fac03232e1410262f87ee786c57",
    bot_token = "5442053935:AAGLySF2qJFta00zW1-RLnkdCiO95ppTtV8"
)

app.on_message(
    filters.command("shell")
    & filters.user(own))
@app.on_edited_message(
    filters.command("shell")
    & filters.user(own))
async def shell(client, message):
    cmd = message.text.split(' ', 1)
    if len(cmd) == 1:
        return await message.reply('No command to execute was given.')
    shell = (await shell_exec(cmd[1]))[0]
    if len(shell) > 3000:
        with open('shell_output.txt', 'w') as file:
            file.write(shell)
        with open('shell_output.txt', 'rb') as doc:
            await message.reply_document(document=doc, file_name=doc.name)
            try:
                os.remove('shell_output.txt')
            except:
                pass
    elif len(shell) != 0:
        await message.reply(shell)
    else:
        await message.reply('No Reply')


@app.on_message(filters.command("pyro") & filters.user(own))
@app.on_edited_message(
    filters.command("pyro")
    & filters.user(own))
async def eval(client, message):
    if len(message.command) < 2:
        return await message.reply("Masukkan kode yang ingin dijalankan..")
    status_message = await message.reply_text("Sedang Memproses Eval...")
    cmd = message.text.split(" ", maxsplit=1)[1]

    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = json.dumps(exc,indent=4)
    elif stderr:
        evaluation = json.dumps(stderr,indent=4)
    elif stdout:
        evaluation = json.dumps(stdout,indent=4)
    else:
        evaluation = "Berhasil"

    final_output = "<b>EVAL</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>OUTPUT</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n"

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "MissKaty_Eval.txt"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[:4096 // 4 - 1],
                disable_notification=True,
                quote=True,
            )
            try:
                os.remove("MissKaty_Eval.txt")
            except:
                pass
    else:
        await reply_to_.reply_text(final_output, quote=True)
    await status_message.delete()

async def aexec(code, client, message):
    exec("async def __aexec(client, message): " +
         "".join(f"\n {l_}" for l_ in code.split("\n")))
    return await locals()["__aexec"](client, message)


async def shell_exec(code, treat=True):
    process = await asyncio.create_subprocess_shell(
        code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)

    stdout = (await process.communicate())[0]
    if treat:
        stdout = stdout.decode().strip()
    return stdout, process


print('Running')
app.run()

