from utils import upload_files, randChar, save_images
from db.crud import image_bundle
from db.schemas import image_bundle as image_bundle_schema
from db.service import users
from constant import BUCKET_URL

def upload_images(db, user_email, images):
    image_bundle_id = randChar(16)
    user = users.get_user_by_email(db, email=user_email)
    paths = upload_files(save_images(images, image_bundle_id), "image", image_bundle_id)

    image_bundle.create_image_bundle(db
        , image_bundle_schema.ImageBundleCreate(image_bundle_id=image_bundle_id,
        user_id=user.user_id,
        image_urls=[BUCKET_URL+path for path in paths]))
    return paths, image_bundle_id
