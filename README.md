Simple script to convert Compose file, as found on Linux, to the
`~/Library/KeyBindings/DefaultKeyBinding.dict` format used on MacOS.

Default `Compose` key is `F13`, so one have to remap some existing key to `F13`
to make the setup work. One option is Karabiner, another one is a built-in tool
called `hidutil`. The following command maps `Right Alt` to `F13`:

```bash
hidutil property --set '{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x7000000E6,"HIDKeyboardModifierMappingDst":0x700000068}]}'
```
List of key codes is available at
[technical note TN2450](https://developer.apple.com/library/archive/technotes/tn2450/_index.html).

This doesn't survive reboot, so one should deploy a plist file to
`~/Library/LaunchAgents/local.RemapRightOptionToF13.plist`.
