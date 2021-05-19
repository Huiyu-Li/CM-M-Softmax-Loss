import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from  torch.utils.data import DataLoader
import torch.optim.lr_scheduler as lr_scheduler
from CMMSoftLoss import CMMSoftLoss
import matplotlib.pyplot as plt
import multiprocessing


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1_1 = nn.Conv2d(1, 32, kernel_size=5, padding=2)
        self.prelu1_1 = nn.PReLU()
        self.conv1_2 = nn.Conv2d(32, 32, kernel_size=5, padding=2)
        self.prelu1_2 = nn.PReLU()
        self.conv2_1 = nn.Conv2d(32, 64, kernel_size=5, padding=2)
        self.prelu2_1 = nn.PReLU()
        self.conv2_2 = nn.Conv2d(64, 64, kernel_size=5, padding=2)
        self.prelu2_2 = nn.PReLU()
        self.conv3_1 = nn.Conv2d(64, 128, kernel_size=5, padding=2)
        self.prelu3_1 = nn.PReLU()
        self.conv3_2 = nn.Conv2d(128, 128, kernel_size=5, padding=2)
        self.prelu3_2 = nn.PReLU()
        self.preluip1 = nn.PReLU()
        self.ip1 = nn.Linear(128*3*3, 2)
        #self.ip2 = nn.Linear(2, 10, bias=False)
        self.ip2 = CMMSoftLoss(2, 10, s=30, m=0)

    def forward(self, x,target):
        x = self.prelu1_1(self.conv1_1(x))
        x = self.prelu1_2(self.conv1_2(x))
        x = F.max_pool2d(x,2)
        x = self.prelu2_1(self.conv2_1(x))
        x = self.prelu2_2(self.conv2_2(x))
        x = F.max_pool2d(x,2)
        x = self.prelu3_1(self.conv3_1(x))
        x = self.prelu3_2(self.conv3_2(x))
        x = F.max_pool2d(x,2)
        x = x.view(-1, 128*3*3)
        ip1 = self.preluip1(self.ip1(x))
        ip2 = self.ip2(ip1,target)
        return ip1, F.log_softmax(ip2, dim=1)

def visualize(feat, labels, epoch):
    plt.ion()
    c = ['#ff0000', '#ffff00', '#00ff00', '#00ffff', '#0000ff',
         '#ff00ff', '#990000', '#999900', '#009900', '#009999']
    plt.clf()
    for i in range(10):
        plt.plot(feat[labels == i, 0], feat[labels == i, 1], '.', c=c[i])
    plt.legend(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], loc = 'upper right')
    #plt.x(xmin=-8,xmax=8)
    #plt.ylim(ymin=-8,ymax=l8)
    import numpy as np
    ffmax = np.max(feat)+1
    plt.xlim(xmin=-ffmax, xmax=ffmax)
    plt.ylim(ymin=-ffmax,ymax=ffmax)


    # plt.x(xmin=-8,xmax=8)
    # plt.ylim(ymin=-8,ymax=l8)
    plt.text(-7.8,7.3,"epoch=%d" % epoch)
    plt.savefig('./images/epoch=%d.jpg' % epoch)
    plt.draw()
    plt.pause(0.001)


def train(epoch):
    print("Training... Epoch = %d" % epoch)
    ip1_loader = []
    idx_loader = []
    for i,(data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        ip1, pred = model(data,target)
        #loss = nllloss(pred, target)
        loss = criterion(pred, target)

        optimizer4nn.zero_grad()
        #optimzer4center.zero_grad()

        loss.backward()

        optimizer4nn.step()
        #optimzer4center.step()

        ip1_loader.append(ip1)
        idx_loader.append((target))

    feat = torch.cat(ip1_loader, 0)
    labels = torch.cat(idx_loader, 0)
    visualize(feat.data.cpu().numpy(),labels.data.cpu().numpy(),epoch)

##################################main#################################################################################
if __name__ == '__main__':
    #freeze_support()
    use_cuda = torch.cuda.is_available() and True
    device = torch.device("cuda" if use_cuda else "cpu")
    # Dataset
    trainset = datasets.MNIST('./MNIST', download=True,train=True, transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))]))
    train_loader = DataLoader(trainset, batch_size=128, shuffle=True, num_workers=4)

    # Model
    model = Net().to(device)

    # NLLLoss
    #nllloss = nn.NLLLoss().to(device) #CrossEntropyLoss = log_softmax + NLLLoss
    criterion = torch.nn.CrossEntropyLoss().to(device)

    # optimzer4nn
    optimizer4nn = optim.SGD(model.parameters(),lr=0.001,momentum=0.9, weight_decay=0.0005)
    sheduler = lr_scheduler.StepLR(optimizer4nn,20,gamma=0.8)

    # optimzer4center
    #optimzer4center = optim.SGD(criterion.parameters(), lr =0.5)

    for epoch in range(100):
        sheduler.step()
        # print optimizer4nn.param_groups[0]['lr']
        train(epoch+1)


