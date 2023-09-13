import torch
import torch.nn as nn
from OCRDataset import OCRDataset
from torchvision.transforms import ToTensor, Resize, Compose
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from model import CRNN
import itertools
import numpy as np

def words_from_labels(labels, char_list):
    """
    converts the list of encoded integer labels to word strings like eg. [12,10,29] returns CAT 
    """
    txt=[]
    for ele in labels:
        if ele == 0: # CTC blank space
            txt.append("")
        else:
            #print(letters[ele])
            txt.append(char_list[ele]+1)
    return "".join(txt)

def decode_batch(test_func, word_batch): #take only a sequence once a time
    """
    Takes the Batch of Predictions and decodes the Predictions by Best Path Decoding and Returns the Output
    """
    out = test_func([word_batch])[0] #returns the predicted output matrix of the model
    ret = []
    for j in range(out.shape[0]):
        out_best = list(np.argmax(out[j, :], 1))
        out_best = [k for k, g in itertools.groupby(out_best)]
        outstr = words_from_labels(out_best)
        ret.append(outstr)
    return ret


if __name__ == '__main__':
    num_epochs = 100
    batch_size = 8
    max_label_len = 16

    transform = Compose([
        Resize((64,128)),
        ToTensor(),
        ])
    
    #split train/val dataset
    dataset = OCRDataset(root = "data", train=True, transform=transform)  # Replace with your dataset
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_dataloader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        num_workers=4,
        drop_last=True,
        shuffle=True
    )

    val_dataloader = DataLoader(
        dataset=val_dataset,
        batch_size=batch_size,
        num_workers=4,
        drop_last=True,
        shuffle=True
    )
    char_list = dataset.char_list
    model = CRNN(num_classes=len(char_list)+1)
    criterion = nn.CTCLoss(blank=0)
    output_lengths = torch.full(size=(batch_size,), fill_value=max_label_len, dtype=torch.long)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    num_iters = len(train_dataloader)
    if torch.cuda.is_available():
        model.cuda()
    for epoch in range(num_epochs):
        model.train()
        for iter, (images, padded_labels, label_lenghts) in enumerate(train_dataloader):
            if torch.cuda.is_available():
                images = images.cuda()
                padded_labels = padded_labels.cuda()
            outputs = model(images)
            #output(sequence_length, batch_size, num_classes)
            #padded_labels(batch_size, max_label_len)
            #output_lengths, label_lenghts(batch_size)
            loss_value = criterion(outputs, padded_labels, output_lengths, label_lenghts)
            optimizer.zero_grad()
            loss_value.backward()
            optimizer.step()
            if (iter+1)%10:
                print("Epoch {}/{}. Iteration {}/{}. Loss{}".format(epoch+1,num_epochs, iter+1, num_iters, loss_value))

        model.eval()
        for iter, (images, padded_labels) in enumerate(val_dataloader):
            if torch.cuda.is_available():
                images = images.cuda()
                padded_labels = padded_labels.cuda()

            with torch.no_grad():
                predictions = model(images)  
                loss_value = criterion(predictions, padded_labels, output_lengths, label_lenghts)          
            


