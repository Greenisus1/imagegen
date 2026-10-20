# Imagegen

AI image generator for the Pi. Type what you want to see, and it is drawn right in your browser. Save the good ones onto the Pi with one click.

## Run

```
bash app-store.sh install
bash app-store.sh run
```

Then open the address it prints (http://localhost:8317 or a free port near it) in the Pi's browser. The page opens on its own when it can.

## How it works

- Drawing happens in your browser with puter.js, a free service. No API key, nothing to install.
- Puter asks you to **sign in with a free Puter account before it will draw**. You make that account yourself with Puter; this app never sees your password. A small Puter window pops up when you press "Sign in with Puter", and after that you just press Generate.
- Your prompt goes to Puter to be drawn. Nothing else leaves the Pi.
- "Save to this Pi" stores the picture as a PNG in the `images` folder next to the app. The page also shows a gallery of everything you have saved.

## Good to know

- Drawing can take up to a minute. If it ever hangs, the app stops waiting after two and a half minutes and tells you.
- Works on any browser that can reach the Pi - the Pi's own browser, or another computer on the same network.
- No API keys, no accounts in the code, and nothing is sent anywhere except your prompt to Puter when you press Generate.

MIT, built with AI assistance from my design.
