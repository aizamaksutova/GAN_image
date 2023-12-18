# GAN_image
Project on Image Generation with VAE and GANs

## How to install?

Make sure to follow this guide
```
git clone https://github.com/aizamaksutova/GAN_image.git
cd Gan_image
pip install -r requirements.txt
```

## How to inference?

To inference a gif from one of my selected runs you should run my inference.ipynb notebook where you will be able to generate a gif manually (it might take very long though, so think twice)


## How to train the model by yourself?
In order to train the model you would need to perform simple steps, but wait for a long time for them to actually download all the data which is a ASV Dataset for antispoofing model training

To train the model on the cats dataset do this:
```
#you need to have a kaggle.json file from your kaggle account
chmod a+x cook_cats.sh
./cook_cats.sh
python3 train.py -c configs/gan_cats.json
```
All the other parameters are manually stored in the config.json, but you can look up the config options in train.py in order to change everything right from terminal.

To train the model on the arts dataset do this:

```
#you need to have a kaggle.json file from your kaggle account
chmod a+x draw_art.sh
./draw_art.sh
python3 train.py -c configs/cvae_train.json
```
## Samples 
You can access the samples for cats here [link](https://drive.google.com/file/d/1t8FWg7C_noHrAIVfH75UoHJCKzkllXQf/view?usp=sharing) or (this choice is better!) in my wandb report

## Wandb report

Here is the [link](https://wandb.ai/aamaksutova/VAE1/reports/Generative-models-for-images--Vmlldzo2Mjk0MjU2?accessToken=f87jl61hihb2s6bt66evq5xipe5e0auk1narun9xt61703a09vkxzparlj647nga) to my wandb report with all the architecture explanation and generated samples

