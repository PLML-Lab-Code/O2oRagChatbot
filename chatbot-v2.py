import gradio as gr
import json
import requests
import os
from text_generation import Client, InferenceAPIClient

# Load pre-trained model and tokenizer - for THUDM model
from transformers import AutoModel, AutoTokenizer

# tokenizer_glm = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
# model_glm = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()

tokenizer_glm = AutoTokenizer.from_pretrained("gpt2")
model_glm = AutoModel.from_pretrained("gpt2").half().cuda()
model_glm = model_glm.eval()

# Load pre-trained model and tokenizer for Chinese to English translator
#from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
#model_chtoen = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
#tokenizer_chtoen = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")


    
# Define function to generate model predictions and update the history
def predict_glm_stream(input, top_p, temperature, history=[]): 
    history = list(map(tuple, history))
    for response, updates in model_glm.stream_chat(tokenizer_glm, input, history, top_p=top_p, temperature=temperature):   
        yield updates 
    
def reset_textbox():
    return gr.update(value="")

def translate_Chinese_English(chinese_text): 
    # translate Chinese to English
    # tokenizer_chtoen.src_lang = "zh"
    # encoded_zh = tokenizer_chtoen(chinese_text, return_tensors="pt")
    # generated_tokens = model_chtoen.generate(**encoded_zh, forced_bos_token_id=tokenizer_chtoen.get_lang_id("en"))
    # trans_eng_text = tokenizer_chtoen.batch_decode(generated_tokens, skip_special_tokens=True)
    # return trans_eng_text[0]
    return chinese_text


title = """<h1 align="center">KNU Test ChatBot No.2</h1>
			<h3 align="center">Layout Test bed (Not working)</h3>"""
header = """<center>Find more about Chatglm-6b on Huggingface at <a href="https://huggingface.co/THUDM/chatglm-6b" target="_blank">THUDM/chatglm-6b</a>, and <a href="https://github.com/THUDM/ChatGLM-6B" target="_blank">here</a> on Github.<center>"""
description = """<br>
"""

theme = gr.themes.Default(#color contructors
                          primary_hue="violet", 
                          secondary_hue="indigo",
                          neutral_hue="purple").set(slider_color="#800080")
                           
with gr.Blocks(css="""#col_container {margin-left: auto; margin-right: auto;}
                #chatglm {height: 520px; overflow: auto;} """, theme=theme ) as demo:
    gr.HTML(title)
    gr.HTML(header)
    with gr.Column(): #(scale=10):
        with gr.Blocks():
            with gr.Row():
                with gr.Column(scale=8):
                    inputs = gr.Textbox(placeholder="Hi there!", label="Type an input and press Enter ⤵️ " )
                with gr.Column(scale=1):
                    b1 = gr.Button('🏃Run', elem_id = 'run')#.style(full_width=True)
                with gr.Column(scale=1):
                    b2 = gr.Button('🔄Clear the Chatbot!', elem_id = 'clear')#.style(full_width=True)
                    state_glm = gr.State([])

        with gr.Blocks():
            chatbot_glm = gr.Chatbot(elem_id="chatglm", label='THUDM-ChatGLM6B')
          
        with gr.Accordion(label="Parameters for ChatGLM-6B", open=False):
            gr.HTML("Parameters for ChatGLM-6B", visible=True)
            top_p = gr.Slider(minimum=-0, maximum=1.0,value=1, step=0.05,interactive=True, label="Top-p", visible=True)
            temperature = gr.Slider(minimum=-0, maximum=5.0, value=1, step=0.1, interactive=True, label="Temperature", visible=True)

    inputs.submit( predict_glm_stream,
                [inputs, top_p, temperature, chatbot_glm ],
                [chatbot_glm],)
    inputs.submit(reset_textbox, [], [inputs])

    b1.click( predict_glm_stream,
                [inputs, top_p, temperature, chatbot_glm ],
                [chatbot_glm],)
    b1.click(reset_textbox, [], [inputs])

    b2.click(lambda: None, None, chatbot_glm, queue=False)
    
    gr.HTML('''<center><a href="https://huggingface.co/spaces/ysharma/ChatGLM-6b_Gradio_Streaming?duplicate=true"><img src="https://bit.ly/3gLdBN6" alt="Duplicate Space"></a>To avoid the queue and for faster inference Duplicate this Space and upgrade to GPU</center>''')
    gr.Markdown(description)
    demo.launch(height= 800, debug=True, max_threads=16)