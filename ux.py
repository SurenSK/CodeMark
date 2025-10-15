import gradio as gr
from wm import encode, decode

with gr.Blocks() as app:
    with gr.Row():
        with gr.Column(scale=1):
            input_func = gr.Textbox(placeholder="input function", lines=10, max_lines=10, show_label=False, container=False)
            payload = gr.Textbox(placeholder="payload", lines=1, max_lines=1, show_label=False, container=False)
            btn_watermark = gr.Button("watermark")
        with gr.Column(scale=1):
            output_func = gr.Textbox(placeholder="watermarked function", lines=10, max_lines=10, show_label=False, container=False)
            detected_payload = gr.Textbox(placeholder="detected payload", lines=1, max_lines=1, show_label=False, container=False)
            btn_detect = gr.Button("detect")
    
    btn_watermark.click(lambda x, y: encode(x, int(y)), [input_func, payload], output_func)
    btn_detect.click(lambda x: (lambda p, m: f"{p} ({m})")(*decode(x, getMax=True)), output_func, detected_payload)

app.launch()