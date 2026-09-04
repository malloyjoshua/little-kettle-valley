# Little Kettle Valley: install guide for friends

Pick the path for your computer. All three end up in the same place — Prism Launcher, signed in with your Microsoft account, with the pack installed and self-updating.

## Windows

1. Download **LittleKettleValley-Setup.exe** from the [release page](https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends) and open it. Your browser will probably flag it as uncommonly downloaded — choose **Keep**.
2. Windows SmartScreen will show a blue "Windows protected your PC" screen with only a **Don't run** button. Click **More info**, then **Run anyway**. This happens because the installer isn't code-signed (no cost was spared, just a fee) — it's a one-time click.
3. Click through **Next → Install**. No admin password, nothing else to install — Java is bundled.
4. Leave **Launch Little Kettle Valley** ticked. The launcher opens and asks you to **sign in with your Microsoft account** — the one that owns Minecraft. That's the only sign-in.
5. Click **Little Kettle Valley → Play**.

*Memory:* nothing to set. The installer reads how much RAM your PC has and picks the right amount for you (3 GB on an 8 GB machine, 3.5 GB on 16 GB, 4 GB above that).

## Mac

1. Download **LittleKettleValley.dmg** from the [release page](https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends) and open it. Three steps are drawn right on the disk image:
   - **Drag Prism Launcher into Applications.** Leave the window open for step 3.
   - **Open Prism Launcher, sign in with your Microsoft account.** It fetches its own Java — let it, that's normal.
   - **Drag the kettle zip onto Prism's window** (or Add Instance > Import). First launch installs the pack.
2. The first time you open Prism Launcher, macOS shows a one-time confirmation — *"Prism Launcher is an app downloaded from the Internet. Are you sure you want to open it?"* Click **Open**. You won't see this again, and you won't need to dig into System Settings — the app is notarized by its own developers.
3. Sign in with your Microsoft account when Prism asks (Accounts, top right, if it doesn't ask automatically).

*Memory:* the instance comes preset to 3072 MB, sized for an 8 GB MacBook Air. If your Mac has 16 GB or more, raise it: select the instance, **Edit → Settings → Memory**, and set the maximum to **3584** (16 GB) or **4096** (32 GB+).

## Manual (any launcher)

Use this if you already run a different launcher, or the Windows/Mac installer doesn't fit your setup.

1. Install **Prism Launcher** (free): https://prismlauncher.org/download/
2. Open Prism. Sign in with your Microsoft account when it asks (Accounts, top right).
3. Download the pack file (`LittleKettleValley.zip`) from the [release page](https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends). Don't unzip it.
4. In Prism: **Add Instance** > **Import** > pick the zip. Click OK.
5. Select the instance, click **Edit** > **Settings**, and set memory: **3072 MB** on an 8 GB machine, **3584 MB** on 16 GB, **4096 MB** on 32 GB. (Measured: the game uses about 1 GB on top of whatever you allocate, so 3072 on an 8 GB machine leaves room for the OS.)
6. Click **Launch**.

*Memory:* the zip ships at **3584 MB**, which suits a 16 GB machine. On an 8 GB machine drop it to **3072** in step 5 — that is the one setting worth getting right.

## First launch

The first launch downloads about 125 mods and takes a few minutes. After that it's fast. Every time you launch after that, the pack checks for updates and applies them — you never need to download anything again.

## Join the server

**Server address:** `cynthia-mfc.tun.ply.gg` (Multiplayer > Add Server, paste that as the address; no port needed). If a launcher insists on a port, use `cynthia-mfc.tun.ply.gg:35925`. The server is up when Josh's Mac is running it.

**Multiplayer** > **Add Server**, address from Josh. Your name has to be on the whitelist first, so send Josh your exact Minecraft username before you try to connect.

## If it won't start
- Make sure memory is set to at least 3072 MB (Edit > Settings > Memory).
- Turn off shaders if any got enabled (Options > Video > Shader Packs > None). The pack ships without them on purpose.
- Send Josh the file `logs/latest.log` from the instance's Minecraft folder (right-click instance > Minecraft Folder).
