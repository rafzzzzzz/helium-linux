# Helium with mouse gestures (unofficial)

An unofficial Linux build of the [Helium Browser](https://github.com/imputnet/helium)
with Vivaldi-style mouse gestures built into the browser: hold the right mouse
button over a page, draw a stroke, release.

> [!IMPORTANT]
> This is a personal fork. It is **not affiliated with or endorsed by Helium
> or imput**, and its builds are not signed with Helium's key. Please don't
> report problems with this build to the Helium project — open an issue here
> instead.

## Also included

- **Up to 20 shortcuts on the new tab page** (Chromium's default is 10), by
  enabling Chromium's built-in shortcuts redesign
  ([`ntp-20-shortcuts.patch`](patches/helium/linux/ntp-20-shortcuts.patch)).

## Why not an extension?

Gesture extensions can't run on `chrome://` pages, the new tab page or pages
that are still loading. On Linux they're also clumsy because Chromium opens the
context menu as soon as the right button is *pressed*, so extensions usually
need a double right-click. Built into the browser, gestures work on every page
and a plain right-click still opens the normal context menu.

## Download

Grab the AppImage or tarball from the
[releases page](https://github.com/rafzzzzzz/helium-linux/releases).
x86_64 only. Builds lag behind official Helium releases, so you'll get security
fixes later than with official Helium.

## Default gestures

| Gesture | Action |
|---|---|
| ← | Back |
| → | Forward |
| ↓ | New tab |
| ↑ | Close tab |
| ↑ ↓ | Reload |
| ↓ → | Bookmarks side panel |
| ← ↓ | Downloads |

A blue trail shows the stroke while you draw.

## Configuring gestures

Open `chrome://flags`, search for **Mouse Gesture Bindings**, enter your
bindings and restart. **Mouse Gestures** in the same page turns the feature
off entirely.

The format is comma-separated `gesture=action` pairs, where a gesture is a
sequence of `L`, `R`, `U`, `D` strokes:

```
L=back,R=forward,D=new-tab,U=close-tab,UD=reload,DR=bookmarks,LD=downloads
```

Setting the flag replaces the defaults, so include every gesture you want.
Invalid entries are skipped (run with `--enable-logging=stderr` to see why).

You can also pass it on the command line:
`helium --helium-mouse-gesture-bindings="L=back,R=forward"`

### Available actions

| Action | Does |
|---|---|
| `back`, `forward` | Navigate history |
| `reload`, `hard-reload`, `stop`, `home` | Page loading |
| `new-tab`, `close-tab`, `restore-tab`, `duplicate-tab`, `pin-tab` | Tabs |
| `next-tab`, `previous-tab` | Switch tabs |
| `new-window`, `new-incognito-window`, `close-window`, `minimize-window` | Windows |
| `fullscreen`, `zoom-in`, `zoom-out`, `zoom-reset` | View |
| `bookmarks` (side panel), `bookmark-manager`, `history`, `downloads` | Pages and panels |
| `devtools`, `toggle-vertical-tabs` | Other |

## How it works

Everything lives in one patch,
[`patches/helium/linux/add-mouse-gestures.patch`](patches/helium/linux/add-mouse-gestures.patch),
applied on top of Helium's own patches. It adds a pre-target event handler to
each browser window that catches right-button drags over web contents before
the page sees them, recognizes the stroke directions and runs the matching
browser command. A right-click without movement is replayed to the page so the
context menu still works.

Mouse gestures are only active over the page area; right-clicking tabs and the
toolbar is unchanged.

## Building

Same as upstream helium-linux: run `scripts/docker-build.sh` from the repo
root (needs Docker, ~100 GB of disk and several hours), then
`package/docker-package.sh` to create the AppImage and tarball under
`build/release/`. See the
[upstream README](https://github.com/imputnet/helium-linux#building) for
details.

## License

GPL-3.0, like Helium. See [LICENSE](LICENSE). Code imported from
ungoogled-chromium keeps its BSD 3-Clause license
([LICENSE.ungoogled_chromium](LICENSE.ungoogled_chromium)). All credit for the
browser itself goes to the [Helium](https://github.com/imputnet/helium) and
[ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium)
projects.
