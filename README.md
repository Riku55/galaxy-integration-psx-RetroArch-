# galaxy-integration-psx-RetroArch-
PSX RetroArch integration for GOG Galaxy 2.0

# [If you want the integration to work, please read the tutorial!](https://github.com/Riku55/galaxy-integration-psx-RetroArch-#tutorial)

This integration is still work in progress, but it's core features are working and the worst bugs are removed, so try it out if you'd like to.
Thanks to AHCoder for using his PS2 integration as base for this one. Also thanks to several people on the GOG Discord for helping me out with some problems.

#### Working Features:
- Enter path for roms in user_config.py and scan the same folder in Retroarch to add them into Galaxy 2.0
- Enter path for emulator and launch roms directly from Galaxy 2.0
- Import play times from RetroArch by enabling "Save runtime log (aggregate)" in RetroArch settings under "Saving"
- Use all available cores, change it in user_config.py. Some cores don't support some file formats so. Use standard if unsure.

## Tutorial

### Setting up [RetroArch](https://retroarch.com/?page=platforms) - You need to repeat step 3 after adding new Roms to the path.
1. Open RetroArch.
2. Navigate to the left until you're at *Main Menu*, click on *Load Core* -> *Download a Core* and select *Sony - PlayStation (PCSX ReARMed)*.
3. Navigate to the right until you're at *Import Content*, click on *Scan Directory*, navigate to the folder where your Roms are and click on *Scan this Directory*.
4. Navigate to *Settings*, click on *Saving*, go to the last option there *Save runtime log (aggregate)* and turn it on.

### Setting up the Integration:
1. Download the integration (use clone or download or download the *Source Code.zip* file in releases or just [click here](https://github.com/Riku55/galaxy-integration-psx-RetroArch-/archive/master.zip)).
2. Extract the ZIP file.
3. Put it into your Galaxy plugin folder (standard is: *C:\Users\USERNAME\AppData\Local\GOG.com\Galaxy\plugins\installed*)
4. Open the file *user_config.py* with an editor.
5. Add your emulator and roms path as described in the file.
6. (Re)start Galaxy 2.0 and connect the integration.
_______________________________________________________________________________________________________________________________________


