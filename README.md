
This fork contains an updated Streamlit GUI which adds more settings than the original version for more control and experimentation. 

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

Next 
```
pip install poetry 
poetry install
poetry shell
```
To Run open anaconda/miniconda terminal : 
*Set your drive letter and path in my case s:/tortoise-tts-fast-GUI*
```
conda activate ttsgui
s:
cd tortoise-tts-fast-GUI
streamlit run app.py
```

To Do :
1. Add remaining settings 
2. Fix files being overwritten
~~3. Fix Download Audio file~~

------------------
Visit the original repo for more info
