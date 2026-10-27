-- Undercover overlay: applied at runtime with `hyprctl eval`, never sourced by
-- hyprland.lua. Normal mode comes back with `hyprctl reload config-only`.

local mainMod = "SUPER"
local menu = "~/.local/bin/undercover menu"

hl.config({
    general = {
        gaps_in = 3,
        gaps_out = 6,
        border_size = 1,
        col = {
            active_border = "rgba(4CC2FFCC)",
            inactive_border = "rgba(80808044)",
        },
    },

    decoration = {
        rounding = 8,
        rounding_power = 2,
        shadow = {
            enabled = true,
            range = 18,
            render_power = 3,
            color = 0x55000000,
        },
        blur = {
            enabled = true,
            size = 8,
            passes = 2,
            vibrancy = 0.1696,
        },
    },
})

hl.animation({ leaf = "windowsIn",  enabled = true, speed = 3,   bezier = "easeOutQuint", style = "slide bottom" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.5, bezier = "linear",       style = "popin 90%" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2,   bezier = "easeOutQuint", style = "fade" })

-- Start menu: same launcher database, Windows-like look.
hl.unbind(mainMod .. " + R")
hl.unbind(mainMod .. " + Space")
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + Space", hl.dsp.exec_cmd(menu))
