import copy
import time
import torch
import random
import os, sys, re
import numpy as np
from torch import nn
from PIL import Image
from torch import optim
from transformers import ViTImageProcessor, ViTModel, ViTForImageClassification

class DataLoader:
    def __init__(self, train_data_dir:str):
        self.vit_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        self.train_data_dir = train_data_dir

    def get_training_images(self):
        '''
        Get a balanced and randomized list of tuples of
        training image file paths and binary class labels.
        '''
        positive_examples = [(f'{self.train_data_dir}/google_images/cats/{filename}', 1.0) for filename in os.listdir(f'{self.train_data_dir}/google_images/cats')] + [(f'{self.train_data_dir}/reddit/cats/{filename}', 1.0) for filename in os.listdir(f'{self.train_data_dir}/reddit/cats')]
        negative_examples = [(f'{self.train_data_dir}/google_images/other/{filename}', 0.0) for filename in os.listdir(f'{self.train_data_dir}/google_images/other')] + [(f'{self.train_data_dir}/reddit/pics/{filename}', 0.0) for filename in os.listdir(f'{self.train_data_dir}/reddit/pics')]
        m = min(len(positive_examples), len(negative_examples))-1
        examples = positive_examples[:m] + negative_examples[:m]
        random.shuffle(examples)
        return examples

    def load_image_tensors(self, image_names:list):
        '''
        Load an image from storage by file path and return
        the image pixel values after being processed by the ViT pre-processor.
        '''
        return self.vit_processor(images=[Image.open(image_name) for image_name in image_names], return_tensors="pt")["pixel_values"]

    def __iter__(self):
        '''
        Iterate through each training example in the dataset.

        :returns: A tuple of (preprocessed_img, training_label)
            where preprocessed_img is a 224x224 tensor of pixels
            and training_label is a binary float tensor with only a single element
        '''
        training_points = self.get_training_images()
        for training_point in training_points:
            try:
                training_img_path = training_point[0]
                training_label = training_point[1]
                preprocessed_img = self.load_image_tensors([training_img_path])
                yield preprocessed_img, np.array([[training_label]], dtype=float)
            except Exception as e:
                print(f'Exception while processing point {training_point}: {e}')
        

class CatClassifier(nn.Module):
    vision_transformer = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
    def __init__(self):
        super(CatClassifier, self).__init__()
        self.linear_hidden = nn.Linear(197*768, 1024)
        self.linear_out = nn.Linear(1024, 1)

    def forward(self, image_tensor):
        '''
        Perform the model forward pass over a tensor of 224x224 image(s) features
        from the ViT Processor
        '''
        img_patch_embeddings = self.vision_transformer(image_tensor, output_hidden_states=True).hidden_states[-1].reshape(image_tensor.shape[0], 197*768)
        hidden_neurons = self.linear_hidden(img_patch_embeddings)
        activated_hidden_neurons = torch.nn.functional.relu(hidden_neurons)
        return self.linear_out(activated_hidden_neurons)
    
    def predict(self, image_tensor):
        return torch.sigmoid(self.forward(image_tensor))
    
def trainModel():
    start = time.time()
    data_loader = DataLoader('data')
    total_imgs = len(data_loader.get_training_images())

    classifier = CatClassifier()
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(classifier.parameters(), lr=0.001)
    TRAIN_EPOCHS = 1

    for i in range(TRAIN_EPOCHS):
        epoch = i+1
        point_counter = 0
        running_loss = 0.0
        print("Epoch: ", epoch)
        for train_x, train_y in data_loader:
            optimizer.zero_grad()
            pred_y = classifier(train_x)
            loss = criterion(pred_y, torch.tensor(train_y, dtype=float))
            loss.backward()
            optimizer.step()
            point_counter += 1
            running_loss += loss.item()
            if point_counter % 100 == 0:
                print("train x", train_x.shape, train_x)
                print("train y", train_y)
                print("pred y", torch.sigmoid(pred_y))
                print("running_loss", running_loss)
                print(str(point_counter) + "/" + str(total_imgs))
        print("Epoch loss:", running_loss)

    torch.save(classifier.state_dict(), "cat-classifier.pt")

    processing_timestamp = time.time()
    print(f'Execution time: {processing_timestamp-start}')

if __name__ == "__main__":
    if sys.argv[1] == "train":
        trainModel()
    elif sys.argv[1] == "inference":
        vit_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        cat_logistic_classifier = CatClassifier()
        cat_logistic_classifier.load_state_dict(torch.load('cat-classifier.pt'))
        cat_logistic_classifier.eval()
        cat_logistic_classifier.vision_transformer.eval()

        with open(sys.argv[2], 'rb') as img_bytes:
            with torch.no_grad():
                img_feats = vit_processor(images=[Image.open(img_bytes).convert('RGB')], return_tensors="pt")["pixel_values"]
                probability = cat_logistic_classifier.predict(img_feats)
                print(probability)
                prediction = float(probability[0][0])
                print(prediction)