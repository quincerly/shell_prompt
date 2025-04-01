# Fancy shell prompt to run from PS1 #

Installation:

To install in user directory on Ubuntu Noble or new requires the --break-system-packages to avoid having to use a virtualenv

1. From the top directory:
    ```
    pip3 install --user . --break-system-packages
    ```

2. Configure bookmarks and server abbreviation by putting an edited copy of shell_prompt.conf in your .config directory in your home directory.

3. Add the following line to your .bashrc
	```
	PS1='$(shell_prompt)'
	```
