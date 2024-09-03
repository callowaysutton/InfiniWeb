from app import app, db
from app.blueprints import web_logic
from app.models import Page

from flask import render_template_string, redirect, request, send_file
from io import BytesIO
from diffusers import StableDiffusionPipeline
import torch, threading

# Load the Stable Diffusion model
model_id = "CompVis/stable-diffusion-v1-4"
pipe = StableDiffusionPipeline.from_pretrained(pretrained_model_name_or_path=model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")  # Use CUDA for faster processing
gpu_semaphore = threading.Semaphore(1) # Use a semaphore to prevent multiple threads from using the GPU at the same time

app.register_blueprint(web_logic.web_logic_bp)

@app.errorhandler(404)
def page_not_found(e):
    # Check to see if there is a period in the path
    if ".jpg" in request.path:
        # Check to see if the path is in the database
        page = Page.query.filter_by(path=request.path).first()

        if page:
            # Render the image from the database
            return send_file(BytesIO(page.content), mimetype='image/png')
        
        print(request.path.replace(".jpg", "").replace("/", " "))
        # Get the prompt from the query parameters
        prompt = request.args.get('prompt', default=request.path.replace(".jpg", "").replace("/", " "))

        # Acquire the semaphore before using the GPU
        with gpu_semaphore:
            # Generate the image
            image = pipe(prompt).images[0]

        # Save the image to a BytesIO object
        img_io = BytesIO()
        image.save(img_io, 'PNG')

        # Save the image to the database with the path and base64 encoding
        new_page = Page(path=request.path, content=img_io.getvalue())
        try:
            db.session.add(new_page)
            db.session.commit()
        except:
            return {"Status": "There was an error saving the image to the database."}, 500
        
        img_io.seek(0)

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    if ".png" in request.path:
        # Check to see if the path is in the database
        page = Page.query.filter_by(path=request.path).first()

        if page:
            # Render the image from the database
            return send_file(BytesIO(page.content), mimetype='image/png')
        
        print(request.path.replace(".png", "").replace("/", " "))
        # Get the prompt from the query parameters
        prompt = request.args.get('prompt', default=request.path.replace(".png", "").replace("/", " "))

        # Acquire the semaphore before using the GPU
        with gpu_semaphore:
            # Generate the image
            image = pipe(prompt).images[0]

        # Save the image to a BytesIO object
        img_io = BytesIO()
        image.save(img_io, 'PNG')

        # Save the image to the database with the path and base64 encoding
        new_page = Page(path=request.path, content=img_io.getvalue())
        try:
            db.session.add(new_page)
            db.session.commit()
        except:
            return {"Status": "There was an error saving the image to the database."}, 500
        
        img_io.seek(0)

        # Return the image as a response
        return send_file(img_io, mimetype='image/png')
    if "." in request.path:
        return {"Status": "Page not allowed."}, 404

    # Check to see if the path is in the database
    page = Page.query.filter_by(path=request.path).first()

    if page:
        # Render the page content from the database
        return render_template_string(page.content)
    else:        
        # Query Groq for the page content
        from groq import Groq

        client = Groq()
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": f"Write the body of an HTML document using Bootstrap 5 classes for styling. You should not write anything outside of the body. Write an informative article, with lots of relative links (starting with a '/'), for the following path: /{request.path}"
                }
            ],
            temperature=1,
            max_tokens=8000,
            top_p=1,
            stream=False,
            stop=None,
        )

        content = completion.choices[0].message.content

        try:
            begin_html_index = content.index("```html")
            end_html_index = content.index("```", begin_html_index + 1)
        except:
            # Reload the page to get a new completion
            return redirect(request.path)

        page_html = """
{% extends 'base.html' %}

{% block title %}IniniWeb{% endblock %}

{% block content %}
"""
        page_html += f"{content[begin_html_index + 7:end_html_index]}"
        page_html += "{% endblock %}"

        # Save the page content to the database
        new_page = Page(path=request.path, content=page_html)
        try:
            db.session.add(new_page)
            db.session.commit()
        except:
            return {"Status": "There was an error saving the page content to the database."}, 500
        
        return render_template_string(page_html)
