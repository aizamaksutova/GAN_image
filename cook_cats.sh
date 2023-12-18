mv kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json

export PATH=/users/aizam/.local/bin${PATH:+:${PATH}}

kaggle datasets download spandan2/cats-faces-64x64-for-generative-models

unzip cats-faces-64x64-for-generative-models.zip
rm cats-faces-64x64-for-generative-models.zip
