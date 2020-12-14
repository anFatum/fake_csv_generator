def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/datasets/{1}'.format(instance.schema.owner.id, filename)
