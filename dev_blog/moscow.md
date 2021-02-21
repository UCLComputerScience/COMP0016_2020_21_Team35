| MoSCoW | Content |
| :---: | ----------- |
| Must Have   | A working IVR that asks questions that require a “Yes” or “No” answer. It gives a triage but does not necessarily redirect the caller for any GP (as this depends on the specific telephony system the GP has).|
| Must Have      | Anyone should be able to call the IVR (will require the GP to have a SIP provider).|
| Must Have      | Has to be able to sit in front of a Mitel System. (Specifically for the Mitel System, it must be able to redirect callers to the Mitel telephony system or a specific telephone number).       |
| Must Have      | We must be able to get a diagram from Voiceflow using the client’s Voiceflow credentials and return the diagram in a JSON format.      |
| Must Have      | We must have software developed to turn this Voiceflow diagram JSON format into an IVR automatically.       |
| Must Have      | We must show on the UI whether the total number of calls into the IVR is equal to the total number of calls being redirected at the end of the IVR.      |
| Must Have      | There must be an input on the UI to allow a user to input their Voiceflow email, password, workspace name and project name.      |
| Must Have      | There must be an input on the UI to change the telephone number (specifically as a must have the specific internal telephone numbers for each of the IVR end results).|
| Should Have      | The only part of the program that will be allowed to access the internet is when retrieving the Voiceflow diagram. Other than this the program should be fully independent of the internet/ cloud services.|
| Should Have      | UI should show the call date, total number of calls and the number of calls going to each end point of the IVR. This will be displayed on the computer where the IVR sits.|
| Should Have      | There should be the option for the receptionist at the GP surgery (or someone else) to input their own recorded messages for the IVR (rather than using the automatic text to speech ones). They will record the messages elsewhere and then using a particular file type (such as .MP3 or .WAV) they will be able to add these in place of the automatic messages.|
| Should Have      | A section of the UI which allows the user to change the telephony system in place as well as relevant redirecting numbers. This will allow GP surgeries with a variety (if not all) telephony systems to use our IVR system easily through the UI settings.|
| Should Have      | A section of the UI should allow us to see specifically why calls were cut off during the IVR if they were. We should be able to specifically see whether the user hung-up during the IVR or if they didn’t get to the end for another reason (such as connection issues).|
| Could Have      | Information from IVR sent to relevant people in the surgery (in the form of reports to the person who the patient is being redirected to).|
| Could Have      | More sophisticated statistical analysis of the data in order to help the GP surgery know where most patients are going through to, the times of day etc. Collecting this into nice formats and reports with graphs that can easily be analysed by someone working at the surgery.|
| Could Have      | Being able to change the JSON file on the Linux machine running the IVR remotely. This would allow a receptionist to much more easily change the IVR.|
| Could Have      | Being able to change the telephony settings of the system remotely.|
| Could Have      | Being able to review reports and statistics of the system remotely.|
| Won't Have      | Not having Alexa integration.|
| Won't Have      | Won’t have a solution and UI to build your own IVR (we’ll just be translating from Voiceflow).|
| Won't Have      | Won’t have our own PBX or IVR solution (we’ll be most likely using Asterisk).|
| Won't Have      | Won’t have our own text to speech model (using external library).|
| Won't Have      | Won’t have our own speech to text model (again, using external library).|
| Won't Have      | Won’t have questions that require more complicated answers (only “Yes” or “No”).|
