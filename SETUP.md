# Setup: two accounts, two clients

## The machine

Use a **Windows 10 or 11 PC directly. Don't use a virtual machine.**

The sniper has to run in the same Windows session as both game clients,
because it detects the game process, brings the buyer window forward and
listens for a global hotkey. A VM adds a layer between all of those and
costs graphics performance. Two clients is a normal setup on one PC.

| | Minimum | Recommended |
|---|---|---|
| RAM | 16 GB | 32 GB |
| GPU | runs PoE comfortably | 8 GB VRAM or more |
| Network | wired | wired |

The memory has to cover two clients, Chrome with about 5 trade tabs, and the app.

**On a Mac:** Apple Silicon has no Boot Camp. Parallels with Windows 11 on
ARM could in principle run it, but it is untested here and PoE would run
under x64 emulation. Use a real Windows PC.

## One-time setup

1. **Two accounts.**
   - **A is the buyer.** It holds the currency and does every purchase.
   - **B** is the account you play on.
2. **Install Python 3.12+** from python.org and tick *Add python.exe to PATH*.
3. **Get the app.**
   - Download the branch ZIP:
     `https://github.com/andrewli8/PoEValdoAssistant/archive/refs/heads/feat/two-client-assist.zip`
   - Unzip it.
   - Copy `.env.example` to `.env`.
4. **Make a sniper Chrome.** Create a desktop shortcut with this target:

   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%LOCALAPPDATA%\ValdoSniperChrome" --disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows --disable-features=IntensiveWakeUpThrottling
   ```

   It opens a separate Chrome that keeps background tabs running at full speed.
   Close every Chrome window the first time you use it.
5. **In the sniper Chrome:**
   - Log into pathofexile.com as **account A only**.
   - Install Tampermonkey.
   - Go to `chrome://extensions`, then *Tampermonkey*, then *Details*, and turn on **Allow User Scripts**.
   - Go to Settings, then *Performance*:
     - Add `pathofexile.com` to *Always keep these sites active*.
     - Turn off Energy Saver.
6. **Double-click `start.bat`.** The first run takes about a minute.
   - In the overlay, click **Install the browser script**, then **Install**.
7. **Open your Valdo live searches** in the sniper Chrome and press *Live search*.
   - When Chrome asks whether the site may access devices on your local network, click **Allow**.

## Every session

1. Start `start.bat`.
2. Open the sniper Chrome. Your live-search tabs should reconnect.
3. Start **client A** on account A and park it in your hideout.
4. Start **client B** on account B.
5. Click into client A and press **Ctrl+Alt+B**. The status strip shows `buyer ✓`.
6. Play on B. When an alert fires, press **`** (backtick). Client A travels and comes to the front.
7. In the seller's shop, press **Ctrl+F**, then **Ctrl+V**, to find the map. Buy it by hand.

If you restart client A, press Ctrl+Alt+B again.

## Check that it works

The status strip should read `N tabs · PoE running · buyer ✓ · Trade prices`.

| What you see | What to do |
|---|---|
| `0 tabs` | Check that Allow User Scripts is on, and reload the trade tabs |
| Console shows `ERR_BLOCKED_BY_LOCAL_NETWORK_ACCESS_CHECKS` | Lock icon, then *Site settings*, then allow *Local network access* for pathofexile.com, then reload |
| `update script` | Click it, then hard-reload the trade tabs (Ctrl+Shift+R) |
| `BUYER LOST` | Client A closed or restarted: click into it and press Ctrl+Alt+B |
| `TRADE API REFUSED US` | Your `POESESSID` in `.env` expired. Replace it or leave it empty |
| Hotkey does nothing | The game isn't detected, or no alert is live |

## Rules this follows

- One key press makes one click on the trade site.
- Nothing types or clicks inside either game client.
- You buy every item by hand.
- GGG staff forum posts allow two clients per PC, one account each. That isn't on an official rules page, so check their current stance yourself.
