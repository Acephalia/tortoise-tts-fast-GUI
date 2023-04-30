## Info 
This fork contains an updated Streamlit GUI which adds generation settings for more control and experimentation. 152334H fork of Tortoise-TTS has the best likeness to imported voices at the moments, in my humble opinion. The mrq version has much better nuances and control but adds an American accent to most of my impported voices that are not fine tuned which was driving me nuts. I just wanted to have the extra settings mrq had on thier gradio UI. I taught mysef some streamlit and python and got the GUI working and fixed a few annoying issues with it along the way. I'm not sure how far I can develop this or keep it updated with my knowledge but for the time being it works. 

![Advanced GUI Settings](https://i.imgur.com/3Pd6EXx.jpg)

## FAQ
1. Will this work on an older 8gb and under card? Yes it will. Just check Low VRAM in the gui.
2. Is the install easy? It relatively is. There is a proper (AHEM!) step by step guide below.

## Prerequisites 
1. CudaToolkit : [Download from here](https://developer.nvidia.com/cuda-11-7-0-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local) and install. Choose custom install and uncheck everything except the cudatoolkit option. Your graphic driver will have more updated drivers for the other components you **DON'T WANT TO CHANGE THAT**.
2. Visual C +  : [Download from here](https://c2rsetup.officeapps.live.com/c2r/downloadVS.aspx?sku=community&channel=Release&version=VS2022&source=VSLandingPage&includeRecommended=true&cid=2030:17d407a1213a47f38d57d3df714567fb) and install. Make sure you select Use in Python

## Installaton
To install on Windows please follow these steps (It was very unclear in the original repo and a lot of users had issues) :
Open a miniconda/anaconda terminal as an administrator
```
conda create --name ttsgui python==3.8
```
```
conda activate ttsgui
```

If you have Tortoise installed before next run : 

```pip uninstall tortoise```

Install Cuda 11 to your environment

```conda install cudatoolkit=11.7```

Next navigate to the drive/folder where you want the tortoise-fast-tts folder to be extracted to. Then run : 

```
git clone https://github.com/Acephalia/tortoise-tts-fast-GUI
cd tortoise-tts-fast-GUI
```
```
conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.7 -c pytorch -c nvidia
```

```pip install -e .```

```pip install git+https://github.com/152334H/BigVGAN.git```


### Run GUI
To Run open anaconda/miniconda terminal : 

```
conda activate ttsgui
s:
cd tortoise-tts-fast-GUI
streamlit run app.py
```
*Set your drive letter and path in my case s:/tortoise-tts-fast-GUI*

## Troubleshooting

##### Poetry Missing
Install Poetry into your environment 
```
conda activate ttsgui
s:
cd tortoise-tts-fast-GUI
pip install poetry 
poetry install
poetry shell
```
*Set your drive letter and path in my case s:/tortoise-tts-fast-GUI*

##### Modules Missing
If you encounter any messages stating xyz module is missing or the likes simply go 
back into your env and run 

```pip install xyz ```

*Replace xyz and repeat till all missing modules are installed.*

## To Do :
1. ~~Add remaining settings~~ 
2. Fix files being overwritten
3. ~~Fix Download Audio file~~
4. `` Fix multiple file download~~

## How To Make Proper Samples For Cloning
Coming Soon

------------------
Visit the [original repo](https://github.com/152334H/tortoise-tts-fast) for more info.
