import sys
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def get_compressed_image(source_image, size, quality=80):
    new_img = Image.open(source_image)
    if new_img.mode != 'RGB':
        new_img = new_img.convert('RGB')
    new_img = new_img.resize(size, Image.ANTIALIAS)
    output = BytesIO()
    new_img.save(output, format='JPEG', quality=quality)
    output.seek(0)
    return InMemoryUploadedFile(output,
                                'ImageField',
                                '%s.jpg' % source_image.name.split('.')[0],
                                'image/jpeg',
                                sys.getsizeof(output),
                                None)

# 1120 x 540
def is_time_between(begin_time, end_time, check_time):
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    # crosses midnight
    return check_time >= begin_time or check_time <= end_time
