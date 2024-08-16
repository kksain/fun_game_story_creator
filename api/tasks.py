from celery import shared_task
from weasyprint import HTML
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from .models import Story
import os


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


@shared_task
def export_story_as_image(story_id):
    story = Story.objects.get(id=story_id)
    contributions = story.contributions.all()

    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.load_default()
    except IOError:
        font = ImageFont.load_default()

    draw.text((10, 10), story.title, fill=(0, 0, 0), font=font)

    y_text = 50
    for contribution in contributions:
        draw.text((10, y_text), f'{contribution.user.username}: {contribution.content}', fill=(
            0, 0, 0), font=font)
        y_text += 30

    directory = os.path.join(settings.MEDIA_ROOT, 'exports/images')
    if not os.path.exists(directory):
        os.makedirs(directory)

    image_file_path = os.path.join(directory, f'story_{story.id}.png')
    img.save(image_file_path)

    story.image_file.name = image_file_path
    story.save()


@shared_task
def export_story_as_pdf(story_id):
    story = Story.objects.get(id=story_id)
    contributions = story.contributions.all()
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

    html_content = f"<h1>{story.title}</h1>"
    for contribution in contributions:
        html_content += f"<p>{contribution.user.username}: {contribution.content}</p>"

    directory = os.path.join(settings.MEDIA_ROOT, 'exports/pdf')
    print(f"Creating directory: {directory}")
    if not os.path.exists(directory):
        os.makedirs(directory)
    pdf_file_path = os.path.join(directory, f'story_{story.id}.pdf')
    print(f"PDF file path: {pdf_file_path}")

    try:
        HTML(string=html_content).write_pdf(pdf_file_path)
        print("PDF generated successfully")
    except Exception as e:
        print(f"Error generating PDF: {e}")

    story.pdf_file.name = pdf_file_path
    story.save()
