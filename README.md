# Radiosonde-decoder
Radiosonde decoder with Python and RS1729 decoder. Not need SOX or Virtual cable. Support RS41, M10, M20 and DFM radiosonde. Only RS41 sonde was logged, because Only RS41 have Payload_ID for now.



*****************************************************************************************************************************************************************************************************************************

External Tools Licensing Notice
This project utilizes external command-line tools that are licensed under the GNU General Public License (GPL):

SoX – Licensed under GPLv2

rtl_fm (from the rtl-sdr package) – Licensed under GPLv2

rs1729 (radiosonde decoders) – Licensed under GPLv3

These tools are used as standalone programs executed via system calls or subprocesses. No GPL-licensed code is included directly in this project's source code, nor are any GPL libraries linked or modified.

As such, this project is not a derivative work of those GPL programs and is not subject to GPL licensing terms. However, users are responsible for complying with the licenses of the external tools they install and use.


****************************************************************************************************************************************************************************************************************************
Included External Tools (GPL Notice) This application uses several external open-source command-line tools, which are bundled in the executable distribution and invoked only via subprocess (i.e., as separate processes). These tools are licensed under the GNU General Public License (GPL), and are not integrated directly into the application's codebase.

The included tools are:

Radiosonde decoders (rs1729)
Files: rs41mod.exe, m10mod.exe, dfm09mod.exe, mXXmod.exe
License: GNU General Public License v3.0
Source code: https://github.com/rs1729/RS
Usage: These tools are used as external decoders and are invoked via subprocess.
Location in application: AppDir\rs\decoders\
Replacement: Users may replace these .exe files with compatible versions from the original repository, as required by the GPLv3 license.
RTL-SDR Tool
rtl_fm.exe

License: GNU GPL v2

Source: https://github.com/rtlsdrblog/rtl-sdr-blog
