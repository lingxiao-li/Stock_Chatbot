# Stock_Chatbot
## Configuration Instructions
## Installation Instructions
There are few online packages need to be installed for this project
### Rasa-NLU
***Prerequisites***<br>
<br>
Make sure the Microsoft VC++ Compiler is installed, so python can compile any dependencies. You can get the compiler from: https://visualstudio.microsoft.com/visual-cpp-build-tools/ Download the installer and select VC++ Build tools in the list.<br>
<br>
***Setting up Rasa NLU***<br>
<br>
**Stable (Recommended)**<br>
The recommended way to install Rasa NLU is using pip which will install the latest stable version of Rasa NLU:<br>
```
pip install rasa_nlu
```
**Latest (Most recent github)**<br>
If you want to use the bleeding edge version you can get it from github:<br>
```
git clone https://github.com/RasaHQ/rasa_nlu.git
cd rasa_nlu
pip install -r requirements.txt
pip install -e .
```
Rasa NLU has different components for recognizing intents and entities, most of these will have some additional dependencies.<br>
When you train your model, Rasa NLU will check if all required dependencies are installed and tell you if any are missing.<br>  

***For more installation information***<br>
Go to https://rasa.com/docs/nlu/installation/<br>

### iexfinance
***Setting up iexfinance***<br>
<br>
**From PyPI with pip (latest stable release):**<br>
```
$ pip3 install iexfinance
```
<br>
**From development repository (dev version):**<br>
If you want to use the bleeding edge version you can get it from github:<br>
```
$ git clone https://github.com/addisonlynch/iexfinance.git
$ cd iexfinance
$ python3 setup.py install
```
<br>
***For more installation information***<br>
Go to https://github.com/addisonlynch/iexfinance<br>
<br>
### wxpy
***Setting up wxpy***<br>
wxpy support Python 3.4-3.6, and 2.7 version<br>
To ensure the package can be installed in different Python version<br>
Replace `pip` in the commond below to `pip3` or `pip2`<br>
<br>
**From PyPI with pip:**<br>
```
pip install -U wxpy
```
<br>
**From douban IO PyPI source (Recommend for users in China mainland):**<br>
```
pip install -U wxpy -i "https://pypi.doubanio.com/simple/"
```
<br>
***For more installation information***<br>
Go to https://wxpy.readthedocs.io/zh/latest/#<br>
<br>
## operating instructions
## a file manifest
## copyright and licensing information
## contact information for the distributor or programmer
## known bugs
## troubleshooting
## credits and acknowledgements
## a changelog
