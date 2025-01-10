import gradio as gr
import requests
import shutil

# # Function to send the file to a remote server
# def send_file_to_server(files):
#     # Define the server URL where the file will be sent
#     server_url = "http://localhost:8000/uploadfile/"  # Replace with the actual server endpoint
#     for file in files:
#         # Prepare the file for the HTTPS POST request
#         with open(file.name, "rb") as f:
#             files = {"file": (file.name, f, "application/pdf")}  # Adjust MIME type if not a PDF
            
#             # Send the POST request with the file
#             response = requests.post(server_url, files=files)
    
#     # Return server's response
#     return f"Server Response: {response.status_code}\n{response.text}"

# # Gradio interface
# io = gr.Interface(
#     fn=send_file_to_server,
#     inputs=gr.File(label="Upload a File", file_count="multiple"),
#     outputs=gr.Textbox(label="Server Response"),
# )

# # Launch the interface
# io.launch()


# Function to handle PDF upload and extract content
def upload_pdf(files):
    # Define the server URL where the file will be sent
    server_url = "http://localhost:8000/uploadfile/"  # Replace with the actual server endpoint
    for file in files:
        # Prepare the file for the HTTPS POST request
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f, "application/pdf")}  # Adjust MIME type if not a PDF
            
            # Send the POST request with the file
            response = requests.post(server_url, files=files)
    
    # Return server's response
    return f"Server Response: {response.status_code}\n{response.text}"

# Function for chatbot to answer questions based on PDF content
def chatbot_response(history, query):
    global pdf_content
    if not pdf_content:
        return history + [(query, "Please upload a PDF file first.")]
    
    # Simple logic: Search for the query in the PDF content
    if query.lower() in pdf_content.lower():
        response = f"Your query matches the following:\n\n{pdf_content[:300]}..."
    else:
        response = "Sorry, I couldn't find anything relevant in the uploaded PDF."
    
    return history + [(query, response)]

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## PDF Upload and Chatbot Interface")
    
    with gr.Row():
        with gr.Column():
            upload_button = gr.File(label="Upload PDF", file_types=[".pdf"], interactive=True, file_count="multiple")
            upload_status = gr.Textbox(label="Upload Status", interactive=False)
        
        with gr.Column():
            chatbot = gr.Chatbot(label="Chatbot")
            user_query = gr.Textbox(label="Your Question")
            send_button = gr.Button("Send")

    # Actions
    upload_button.change(upload_pdf, inputs=upload_button, outputs=upload_status)
    send_button.click(chatbot_response, inputs=[chatbot, user_query], outputs=chatbot)

# Launch the Gradio interface
demo.launch()
