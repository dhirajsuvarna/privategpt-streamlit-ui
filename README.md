# Streamlit UI for PrivateGPT 

This is a UI build using `streamlit` which provides as an alternative to the default Gradio UI shipped with [PrivateGPT](https://github.com/imartinez/privateGPT)

# How to make it work 

## Install PrivateGPT 
- Follow the installation steps mentioned in the [official PrivateGPT docs](https://docs.privategpt.dev/installation) 
- Run PrivateGPT project by executing the command  `poetry run python -m private_gpt` as mentioned in the doc. 
- In case you have installe PrivatedGPT along with the default UI. Disable the UI by changing the settings in `settings.yaml`

## Install PrivateGPT-Streamlit-UI
- Clone the project
- Install the dependencies using `poetry install`
- Run the UI using `streamlit run demo.py`
- The PrivateGPT Server URL is set in the `constants.py` file. Change it to point it to the correct Server if necessary. 


