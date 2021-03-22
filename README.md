# GP IVR Software package

GP IVR is a piece of software that allows the automatic creation of an IVR, from a Voicefiles project or file. Analytics and IVR information can then be monitored using the UI.

Closely integrated with both Twilio and Voiceflow. Once an IVR has been created from a Voiceflow project, you can then integrate that with your Twilio number and settings. This will allow users to call the twilio number, be redirected to the IVR and then redirected to a different number, depending on their responses.

Currently we have only tested this thoroughly with Twilio, but in theory any SIP telephone provider should work as long as you can create a SIP trunk with them.

# Requirements

We have mostly tested this on Ubuntu 20.04 LTS and it's recommended you use this or another version of Ubuntu if you can. Although the program can be run on Windows and OSX, it will not be secure and it not advised. This is due to a current issue with Docker port forwarding on Widnows and OSX operating systems.

In order to run the program, you will need to install docker on the machine. Most of the testing was done with version **20.10.3** and it's recommended you use this or a later version if you have difficulties running the program.
This guide works well for installing Docker:
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04

You also need to give the user running the program privilages to run docker commands as if root.
Read https://docs.docker.com/engine/install/linux-postinstall/ on how to do this.

In order to run a deb package easily, you may also want to install gdebi if it's not installed, however it is not necessary.

# How to build

Unforunately the fully built package was too large for github (300 MB) - you can download it from https://sourceforge.com/projects/gp-ivr

Or you can build it with the following:

While in the COMP0016_2020_21_Team35 directory run:

```sh
pyinstaller --onefile --windowed --add-data /usr/local/lib/python3.8/dist-packages/librosa/util/example_data:librosa/util/example_data --hidden-import="sklearn.utils._weight_vector" --hidden-import="scipy.special.cython_special" ui_modules/UI.py
```
In order to run this command you will need all the python libraries required by the project.

This will create a UI executable in a dist folder. Make sure you move the UI exe into COMP0016_2020_21_Team35 directory. Then you can run it simply with:

```sh
./UI
```

Or if you want to build it as a deb package, move the UI executable into COMP0016_2020_21_Team35/gp_ivr_0.0_all/usr/bin/gp_ivr/

Then you can change back to the COMP0016_2020_21_Team35 directory and build the deb package with:

```sh
dpkg-deb --build  gp_ivr_0.0_all/
```

You will then have a deb package that can be installed on an Ubuntu PC or server. This is the same package currently on sourceforge.

# Using or Deploying the Program

If you want more information on how to use the system or how to deploy the system on an Ubuntu PC or Linode server, please refer to out deployment_guide.pdf and user_guide.pdf in the repository.
