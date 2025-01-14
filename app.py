# AGPL: a notification must be added stating that changes have been made to that file.

import os
import subprocess
import shutil
from pathlib import Path
import time
import base64
import random
import streamlit as st
# Set the title of the app
st.set_page_config(page_title="Tortoise TTS Fast GUI")
from random import randint
import numpy as np
import json

from tortoise.api import MODELS_DIR

from tortoise.inference import (
    infer_on_texts,
    run_and_save_tts,
    split_and_recombine_text,
)
from tortoise.utils.diffusion import SAMPLERS
from app_utils.filepicker import st_file_selector
from app_utils.conf import TortoiseConfig

from app_utils.funcs import (
    timeit,
    load_model,
    list_voices,
    load_voice_conditionings,
)


LATENT_MODES = [
    "Tortoise original (bad)",
    "average per 4.27s (broken on small files)",
    "average per voice file (broken on small files)",
]

def main():
    conf = TortoiseConfig()
    
    st.title("Tortoise Fast GUI")
    
    with st.expander("Create New Voice", expanded=False):
        if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = str(randint(1000, 100000000))
            st.session_state["text_input_key"] = str(randint(1000, 100000000))

        uploaded_files = st.file_uploader(
            "Upload Audio Samples for a New Voice",
            accept_multiple_files=True,
            type=["wav"],
            key=st.session_state["file_uploader_key"]
        )

        voice_name = st.text_input(
            "New Voice Name",
            help="Enter a name for your new voice.",
            value="",
            key=st.session_state["text_input_key"]
        )

        create_voice_button = st.button(
            "Create Voice",
            disabled = ((voice_name.strip() == "") | (len(uploaded_files) == 0))
        )
        if create_voice_button:
            st.write(st.session_state)
            with st.spinner(f"Creating new voice: {voice_name}"):
                new_voice_name = voice_name.strip().replace(" ", "_")

                voices_dir = f'./tortoise/voices/{new_voice_name}/'
                if os.path.exists(voices_dir):
                    shutil.rmtree(voices_dir)
                os.makedirs(voices_dir)

                for index, uploaded_file in enumerate(uploaded_files):
                    bytes_data = uploaded_file.read()
                    with open(f"{voices_dir}voice_sample{index}.wav", "wb") as wav_file:
                        wav_file.write(bytes_data)

                st.session_state["text_input_key"] = str(randint(1000, 100000000))
                st.session_state["file_uploader_key"] = str(randint(1000, 100000000))
                st.experimental_rerun()

    with st.expander("Generate Conditioning Latent", expanded=False):                                                                                                        
        # Define the list of voices                                                                                                                                          
        voices = [v for v in os.listdir("tortoise/voices") if v != "cond_latent_example"]                                                                                    
                                                                                                                                                                             
        # Define the list of options for the dropdown menu                                                                                                                   
        options = ["Generate Latent"] + voices                                                                                                                               
                                                                                                                                                                             
        # Create the dropdown menu, radio button group, and "Execute" button                                                                                                 
        choice = st.selectbox("Select a voice to generate the latent for", options)                                                                                          
        if choice != "Generate Latent":                                                                                                                                      
            latent_averaging_mode = st.radio("Latent Averaging Mode", [0, 1, 2], index=1)                                                                                    
            if st.button("Execute"):                                                                                                                                         
                # Call the script to generate the conditioning latent                                                                                                        
                st.write(f"Generating latent for {choice}...")                                                                                                               
                process = subprocess.run(                                                                                                                                    
                    ["python", "scripts/get_conditioning_latents.py", "--voice", choice, "--latent_averaging_mode", str(latent_averaging_mode)],                             
                    capture_output=True,  # capture both standard output and standard error                                                                                  
                    text=True,  # decode the output to a string                                                                                                              
                )                                                                                                                                                            
                if process.returncode == 0:                                                                                                                                  
                    st.write("Latent generated successfully!")                                                                                                               
                    st.code(process.stdout)                                                                                                                                  
                else:                                                                                                                                                        
                    st.write(f"Error generating latent: {process.stderr}")                                                                                                   
                                                                                                                                                                            
                                                                                                                                                                            
      
    text = st.text_area(
        "Text",
        help="Text to speak.",
        value="The expressiveness of autoregressive transformers is literally nuts! I absolutely adore them.",
    )

    def refresh_voices():
        global voices
        voices = [v for v in os.listdir("tortoise/voices") if v != "cond_latent_example"]

    voices = [v for v in os.listdir("tortoise/voices") if v != "cond_latent_example"]                                                                                                      
                                                                                                                                                                                           
    voice = st.selectbox(                                                                                                                                                                  
        "Voice",                                                                                                                                                                           
        voices,                                                                                                                                                                            
        help="Selects the voice to use for generation. See options in voices/ directory (and add your own!) "                                                                              
        "Use the & character to join two voices together. Use a comma to perform inference on multiple voices.",                                                                           
        index=0,                                                                                                                                                                           
    )  
    # Add a "Refresh" link
    if st.button("Refresh"):                                                                                                                    
        refresh_voices()                                                                                                                       
    
    with st.expander("Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            """#### Model parameters"""
            candidates = st.number_input(
                "Candidates",
                help="How many output candidates to produce per-voice.",
                value=1,
            )
            latent_averaging_mode = st.radio(
                "Latent averaging mode",
                LATENT_MODES,
                help="How voice samples should be averaged together.",
                index=0,
            )
            sampler = st.radio(
                "Sampler",
                #SAMPLERS,
                ["dpm++2m", "p", "ddim"],
                help="Diffusion sampler. Note that dpm++2m is experimental and typically requires more steps.",
                index=1,
            )
            
        with col2:
            """#### Optimizations"""
            high_vram = not st.checkbox(
                "Low VRAM",
                help="Re-enable default offloading behaviour of tortoise",
                value=True,
            )
            
            voice_fixer = st.checkbox(
                "Voice fixer",
                help="Use `voicefixer` to improve audio quality. This is a post-processing step which can be applied to any output.",
                value=True,
            )
            
            half = st.checkbox(
                "Half-Precision",
                help="Enable autocast to half precision for autoregressive model",
                value=False,
            )
            kv_cache = st.checkbox(
                "Key-Value Cache",
                help="Enable kv_cache usage, leading to drastic speedups but worse memory usage",
                value=True,
            )
            cond_free = st.checkbox(
                "Conditioning Free",
                help="Force conditioning free diffusion",
                value=True,
            )
            no_cond_free = st.checkbox(
                "Force Not Conditioning Free",
                help="Force disable conditioning free diffusion",
                value=False,
            )

            """#### Text Splitting"""
            min_chars_to_split = st.number_input(
                "Min Chars to Split",
                help="Minimum number of characters to split text on",
                min_value=50,
                value=200,
                step=1,
            )
            
    with st.expander("Load preset"):
        presets = {}
        try:
            with open("presets.json", "r") as f:                   
                presets = json.load(f)
        except FileNotFoundError:
            st.warning("No presets found.")
    
        preset_names = list(presets.keys())                      
        if not preset_names:
            st.warning("No presets found.")
        else:
            preset_name = st.selectbox("Choose a preset", preset_names)                                         
    
        col1, col2 = st.columns(2)
        with col1:
            # Update the values displayed in the GUI with the selected preset                                                        
            if st.button("Load preset"):
                preset_values = presets[preset_name]
                st.session_state.num_autoregressive_samples = preset_values.get("num_autoregressive_samples", st.session_state.num_autoregressive_samples)                   
                st.session_state.diffusion_temperature = preset_values.get("diffusion_temperature", st.session_state.diffusion_temperature)
                st.session_state.diffusion_iterations = preset_values.get("diffusion_iterations", st.session_state.diffusion_iterations)
                st.session_state.seed = preset_values.get("seed", st.session_state.seed)
                st.session_state.cvvp_amount = preset_values.get("cvvp_amount", st.session_state.cvvp_amount)
                st.session_state.top_p = preset_values.get("top_p", st.session_state.top_p)
                st.session_state.temperature = preset_values.get("temperature", st.session_state.temperature)
                st.session_state.length_penalty = preset_values.get("length_penalty", st.session_state.length_penalty)
                st.session_state.repetition_penalty = preset_values.get("repetition_penalty", st.session_state.repetition_penalty)
                st.session_state.cond_free_k = preset_values.get("cond_free_k", st.session_state.cond_free_k)
    
                # Display a message confirming that the preset has been loaded            
                st.success(f"Preset '{preset_name}' loaded!")
        with col2:        
         # Add a button to delete the selected preset                                                                                                                                                                         
            if st.button("Delete preset"):                                                                                                                                                                                                  
                del presets[preset_name]                                                                                                                                                    
                with open("presets.json", "w") as f:                                                                                                                                                                                      
                   json.dump(presets, f)                                                                                                                                                                                      
                st.success(f"Preset '{preset_name}' deleted!")                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                                
    # Initialize session state variables
    if "num_autoregressive_samples" not in st.session_state:
        st.session_state.num_autoregressive_samples = 10
    if "diffusion_temperature" not in st.session_state:
        st.session_state.diffusion_temperature = 1.0
    if "diffusion_iterations" not in st.session_state:
        st.session_state.diffusion_iterations = 30
    if "seed" not in st.session_state:
        st.session_state.seed = -1
    if "cvvp_amount" not in st.session_state:
        st.session_state.cvvp_amount = 0.0
    if "top_p" not in st.session_state:
        st.session_state.top_p = 0.8
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.5
    if "length_penalty" not in st.session_state:
        st.session_state.length_penalty = 2.0                             
    if "repetition_penalty" not in st.session_state:                             
        st.session_state.repetition_penalty = 4.0  
    if "cond_free_k" not in st.session_state:                             
        st.session_state.cond_free_k = 2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
            
    with st.expander("Advanced" , expanded=True):
        col1, col2 = st.columns(2)
        with col1:        
            
            num_autoregressive_samples = st.number_input(                                                                        
                "Samples",                                                                                                       
                help="Number of samples taken from the autoregressive model, all of which are filtered using CLVP. As Tortoise is a probabilistic model, more samples means a higher probability of creating something great.",
                step=1,                                                                                                          
                value=st.session_state.get("num_autoregressive_samples", 10),  # Use the current session state value or default to 10                                                                                                        
            )                                                                                                                    
                                                                                                                                 
            diffusion_temperature = st.number_input(
                "Diffusion Temperature",
                help="Controls the variance of the noise fed into the diffusion model. Values at 0 are the mean prediction of the diffusion network and will sound bland and smeared.",
                step=0.1,
                min_value=0.0,
                max_value=1.0,
                format="%0.1f",
                value=st.session_state.get("diffusion_temperature", 1.0),  # Use the current session state value or default to 1.0
                
            )      
            
            diffusion_iterations = st.number_input(
            "Iterations",
             help="Number of diffusion steps to perform. [0,4000]. More steps means the network has more chances to iteratively refine the output, which should theoretically mean a higher quality output. Generally a value above 250 is not noticeably better,however.",
             step=1,
             value=st.session_state.get("diffusion_iterations", 30),  # Use the current session state value or default to 30
             )
                
            seed = st.number_input(
                "Seed",
                help="Random seed which can be used to reproduce results.",
                value=-1,
            )
            
           
            if seed == -1:
                seed = random.randint(1, 922337203)
            elif seed == 0:
                seed = None

            cvvp_amount = st.number_input(
                "CVVP",
                help="cvvp amount",
                step=0.1,
                min_value=0.0,
                max_value=1.0,
                format="%0.1f",
                value=st.session_state.get("cvvp_amount", 0.0),  # Use the current session state value or default to 0.0
            )

        with col2:       
                                               
            top_p = st.number_input(
                "Top P",
                help="Variation in voice. Boring to crazy",
                step=0.1,
                min_value=0.0,
                max_value=1.0,
                format="%0.1f",
                value=st.session_state.get("top_p", 0.8),  # Use the current session state value or default to 0.8
                
            )
            
            temperature = st.number_input(
                "Temperature",
                help="",
                step=0.1,
                min_value=0.0,
                max_value=1.0,
                format="%0.1f",
                value=st.session_state.get("temperature", 0.5),  # Use the current session state value or default to 0.5
                
            )
            
            length_penalty = st.number_input(
                "Length Penalty",
                help="",
                step=0.1,
                min_value=0.0,
                max_value=8.0,
                format="%0.1f",
                value=st.session_state.get("length_penalty", 2.0),  # Use the current session state value or default to 2.0
                
            )
            
                   
                                                                                                                          
            repetition_penalty = st.number_input(
                "Repetition Penalty",
                help="",
                step=0.1,
                min_value=0.0,
                max_value=8.0,
                format="%0.1f",
                value=st.session_state.get("repetition_penalty", 4.0),  # Use the current session state value or default to 4.0
                
            )         
            
            cond_free_k = st.number_input(
                "Cond Free K",
                help="Balance the conditioning free signal with the conditioning present signal.",
                step=1,
                min_value=1,
                max_value=4,
                value=st.session_state.get("cond_free_k", 2),  # Use the current session state value or default to 2
                
            )                                                                                                   

    
    with st.expander("Save Preset" , expanded=False):
    
        # Add a button to save the settings as a preset
            preset_name = st.text_input("Enter a name for the preset", value="", max_chars=50)
            if st.button("Save preset"):
                if not preset_name:
                    st.warning("Please enter a name for the preset.")
                else:
                    presets = {}
                    try:
                        with open("presets.json", "r") as f:
                            presets = json.load(f)
                    except FileNotFoundError:
                        pass
                    presets[preset_name] = {
                        "num_autoregressive_samples": num_autoregressive_samples,
                        "diffusion_temperature": diffusion_temperature,
                        "diffusion_iterations": diffusion_iterations,
                        "seed": seed,
                        "cvvp_amount": cvvp_amount,
                        "top_p": top_p,
                        "temperature": temperature,
                        "length_penalty": length_penalty,
                        "repetition_penalty": repetition_penalty,
                        "cond_free_k": cond_free_k,
                    }
                    with open("presets.json", "w") as f:
                        json.dump(presets, f)
                    st.success(f"Preset '{preset_name}' saved!")
        
        
        
                                                                                                                                                                     
        
    with st.expander("Other" , expanded=True):                                                                                                      
        col1, col2 = st.columns(2)
        with col1:        
            
            """#### Directories"""
            output_path = st.text_input(
                "Output Path", help="Where to store outputs.", value="results/"
            )
        
        with col2:
        
            """#### Debug"""
            produce_debug_state = st.checkbox(
                "Produce Debug State",
                help="Whether or not to produce debug_state.pth, which can aid in reproducing problems. Defaults to true.",
                value=True,
            )                        
                                                                                                                                                
    ar_checkpoint = "."                                                                                                                                  
    diff_checkpoint = "." 
    if st.button("Update Basic Settings"):
        conf.update(
            EXTRA_VOICES_DIR="S:\tortoise-tts-fast\tortoise\Extra",
            LOW_VRAM=not high_vram,
            AR_CHECKPOINT=ar_checkpoint,
            DIFF_CHECKPOINT=diff_checkpoint,
        )

    ar_checkpoint = None
    diff_checkpoint = None
    tts = load_model(MODELS_DIR, high_vram, kv_cache, ar_checkpoint, diff_checkpoint)

    if st.button("Start"):
        assert latent_averaging_mode
        assert voice

              
        def show_generation(fp, filename: str): 
            with open(fp, "rb") as f: 
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/wav") 
            def download():
                with open(fp, "rb") as f:
                    audio_bytes = f.read()
                b64 = base64.b64encode(audio_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download sample</a>'
                return href
            st.markdown(download(), unsafe_allow_html=True)
        
        
        
        
        with st.spinner(
            f"Generating {candidates} candidates for voice {voice} (seed={seed}). You can see progress in the terminal"
        ):
            nullable_kwargs = {
                        k: v
                        for k, v in zip(
                            ["sampler", "cond_free"],
                            [sampler,  cond_free],
                        )
                        if v is not None
                    }
            os.makedirs(output_path, exist_ok=True)
        
            selected_voices = voice.split(",")
            for k, selected_voice in enumerate(selected_voices):
                if "&" in selected_voice:
                    voice_sel = selected_voice.split("&")
                else:
                    voice_sel = [selected_voice]
                voice_samples, conditioning_latents = load_voice_conditionings(
                    voice_sel, []
                )
        
                voice_path = Path(os.path.join(output_path, selected_voice))
        
                with timeit(
                    f"Generating {candidates} candidates for voice {selected_voice} (seed={seed})"
                ):
                    nullable_kwargs = {
                        k: v
                        for k, v in zip(
                            ["sampler", "cond_free"],
                            [sampler, cond_free],
                        )
                        if v is not None
                    }

                    def call_tts(text: str):           
                        return tts.tts_custom(           
                            text,           
                            k=candidates,           
                            voice_samples=voice_samples,           
                            conditioning_latents=conditioning_latents,           
                            use_deterministic_seed=seed,           
                            return_deterministic_state=True,           
                            num_autoregressive_samples=num_autoregressive_samples,           
                            diffusion_temperature=diffusion_temperature,           
                            cvvp_amount=cvvp_amount,           
                            half=half,           
                            latent_averaging_mode=LATENT_MODES.index(latent_averaging_mode),           
                            top_p=top_p,
                            temperature=temperature,
                            diffusion_iterations=diffusion_iterations,
                            repetition_penalty=repetition_penalty,
                            length_penalty=length_penalty,      
                            cond_free_k=cond_free_k,   
                        )           
                               
                    
                    if len(text) < min_chars_to_split:
                        filepaths = run_and_save_tts(
                            call_tts,
                            text,
                            voice_path,
                            return_deterministic_state=True,
                            return_filepaths=True,
                            voicefixer=voice_fixer,
                        )
                        for i, fp in enumerate(filepaths):
                            show_generation(fp, f"{selected_voice}-text-{i}.wav")
                    else:
                        desired_length = int(min_chars_to_split)
                        texts = split_and_recombine_text(
                            text, desired_length, desired_length + 100
                        )
                        filepaths = infer_on_texts(
                            call_tts,
                            texts,
                            voice_path,
                            return_deterministic_state=True,
                            return_filepaths=True,
                            lines_to_regen=set(range(len(texts))),
                            voicefixer=voice_fixer,
                        )
                        for i, fp in enumerate(filepaths):
                            show_generation(fp, f"{selected_voice}-text-{i}.wav")
        if produce_debug_state:
            """Debug states can be found in the output directory"""


if __name__ == "__main__":
    main()
