import gdown

# a checkpoint
id_model = "1BLJ4xgsyO44X7sMHPwlgrUee3MQiVfaa"
output_model = "model_dcgan.pth"
gdown.download(id=id_model, output=output_model, quiet=False)
