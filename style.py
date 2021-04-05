import sublime
import sublime_plugin


_defaults = None
_applying = False


def settings():
    return sublime.load_settings("Preferences.sublime-settings")


def defaults():
    global _defaults
    if not _defaults:
        _defaults = settings().to_dict()
    return _defaults


def changeset(style):
    target_style = sublime.ui_info()["system"]["style"] if style == "auto" else style
    inverse_style = "dark" if target_style == "light" else "light"

    style_settings = dict(dark=dict(), light=dict(), current=dict())
    for key, value in settings().to_dict().items():
        for mode in ["dark", "light"]:
            prefix = mode + "_"
            if key.startswith(prefix):
                key = key[len(prefix) :]
                style_settings[mode][key] = value
                style_settings["current"][key] = settings().get(key)
                break

    changes = dict()
    for key, current_value in style_settings["current"].items():
        if key in style_settings[target_style]:
            actual_value = style_settings[target_style][key]
            if style == "auto" and key in ["theme", "color_scheme"]:
                actual_value = "auto"
            if current_value != actual_value:
                changes[key] = actual_value
        elif key in style_settings[inverse_style]:
            default_value = defaults()[key]
            if current_value != default_value:
                changes[key] = defaults()[key]

    return changes


def apply(style):
    global _applying

    if not _applying:
        _applying = True

        changes = changeset(style)

        if style != settings().get("style"):
            changes["style"] = style

        if changes:
            print("[sublime-style] changeset:", changes)
            settings().update(changes)
            sublime.save_settings("Preferences.sublime-settings")

        _applying = False


class ToggleStyleCommand(sublime_plugin.ApplicationCommand):
    def run(self, style):
        apply(style)


def plugin_loaded():
    settings().add_on_change("sublime-style", lambda: apply(settings().get("style", "auto")))


def plugin_unloaded():
    settings().clear_on_change("sublime-style")
