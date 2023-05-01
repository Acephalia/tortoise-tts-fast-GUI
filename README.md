
## Info 
This fork contains a completely reworked Streamlit GUI. The 152334H fork of Tortoise-TTS has the best likeness to imported voices at the moment, in my humble opinion. The [mrq version](https://git.ecker.tech/mrq/ai-voice-cloning) has much better nuances and control but adds an American accent to most of my imported voices that are not fine tuned which was driving me nuts. I started working on this because I just wanted to have the extra settings mrq had on their Gradio UI. So I taught myself some Streamlit and python and got the GUI working. I've also fixed a few annoying issues along the way and added some extra features. I'm not sure how far I can develop this or keep it updated with my knowledge but for the time being it works. 

## Features
- Fully reworked GUI 
- Fully control all generation parameters.
- Generate and dump conditioning latent for faster generations or for use with other ML models. 
- Download multiple generated candidates. 

## Screenshots 
![Advanced GUI Settings](https://i.imgur.com/rR5TWg4.jpg)

## FAQ
1. **Will this work on an older 8gb and under card?** Yes it will. Just check Low VRAM in the gui.
2. **Is the install easy?** It relatively is. There is a proper (AHEM!) step by step guide below.
4. **Can I save conditional latents?** Yes you can!

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
2. Fix files being overwritten in results folder
3. ~~Fix Download Audio file~~
4. ~~Fix multiple candidate download~~
5. ~~Add voice refresh~~
6. ~~Add GUI to create and download conditional latents~~
7. ~~Automatically create conditional latents in voice folder~~

## How To Make Proper Samples For Cloning
Coming Soon

------------------
Visit the [original repo](https://github.com/152334H/tortoise-tts-fast) for more info.
