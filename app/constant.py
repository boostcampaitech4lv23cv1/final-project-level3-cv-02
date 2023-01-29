default_dict = dict(
    output_path = "./",
    use_tf = False,
    without_deskew = True,
    save_cache = False
)

fast_only_dict = dict(thresh = 512, step_size = 256)
slow_only_dict = dict(thresh = 1024,step_size = 128)

fast_dict = {**default_dict, **fast_only_dict}
slow_dict = {**default_dict, **slow_only_dict}

paths = {'img_path': '/Users/yj/Projects/maestro/images',
         'xml_path': '/Users/yj/Projects/maestro/xml',
         'mp3_path': '/Users/yj/Projects/maestro/sound'}
