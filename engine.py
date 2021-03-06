import torch
import numpy as np
from tqdm import tqdm
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


def loss_fn(y_pred, y_true):
    lfn = torch.nn.CrossEntropyLoss()
    loss = lfn(y_pred, y_true.flatten())
    return loss


def multi_acc(y_pred, y_true):
    y_pred_softmax = torch.log_softmax(y_pred, dim=1)
    _, y_pred_tags = torch.max(y_pred_softmax, dim=1)

    correct_pred = (y_pred_tags == y_true).float()
    acc = correct_pred.sum() / len(correct_pred)

    acc = torch.round(acc) * 100

    return acc


def get_one_hot(targets, device, n_labels):
    return (torch.eye(n_labels)[targets]).to(device)


def train_fn(data_loader, model, optimizer, device, scheduler):
    """
    train_fn train a model

    Given a dataloader, model, optimizer, device and scheduler train the model.

    Parameters
    ----------
    data_loader : torch.Dataloader
        torch data loader
    model : torch.model
        torch model
    optimizer : torch.optimizer
        torch optimizer
    device : str
        device
    scheduler : torch.scheduler
        torch scheduler

    Returns
    -------
    float
        final loss
    """
    model.train()
    train_epoch_loss = 0
    train_epoch_acc = 0
    for data in tqdm(data_loader, total=len(data_loader)):
        for k, v in data.items():
            data[k] = v.to(device)
        optimizer.zero_grad()
        output = model(**data)

        train_loss = loss_fn(output, data["target_tag"])
        # train_acc = multi_acc(output, data["target_tag"])

        train_loss.backward()
        optimizer.step()
        scheduler.step()

        train_epoch_loss += train_loss.item()
        # train_epoch_acc += train_acc.item()

    return train_epoch_loss / len(data_loader), train_epoch_acc / len(data_loader)


def eval_fn(data_loader, model, device):
    """
    eval_fn evaluate a model

    given a model, dataloader and device get loss

    Parameters
    ----------
    data_loader : torch.dataloader
        dataloader
    model : torch.model
        model
    device : str
        torch device

    Returns
    -------
    float
        final loss
    """
    model.eval()
    train_epoch_loss = 0
    train_epoch_acc = 0
    for data in tqdm(data_loader, total=len(data_loader)):
        for k, v in data.items():
            data[k] = v.to(device)
        output = model(**data)

        train_loss = loss_fn(output, data["target_tag"])
        # train_acc = multi_acc(output, data["target_tag"])

        train_epoch_loss += train_loss.item()
        # train_epoch_acc += train_acc.item()

    return train_epoch_loss / len(data_loader), train_epoch_acc / len(data_loader)


def eval_fn_with_report(data_loader, model, device, enc_tag):
    """
    eval_fn evaluate a model

    given a model, dataloader and device get loss

    Parameters
    ----------
    data_loader : torch.dataloader
        dataloader
    model : torch.model
        model
    device : str
        torch device

    Returns
    -------
    float
        final loss
    """
    model.eval()
    train_epoch_loss = 0
    train_epoch_acc = 0
    y_trues = []
    y_preds = []
    for data in tqdm(data_loader, total=len(data_loader)):
        for k, v in data.items():
            data[k] = v.to(device)
        output = model(**data)

        train_loss = loss_fn(output, data["target_tag"])
        # train_acc = multi_acc(output, data["target_tag"])

        train_epoch_loss += train_loss.item()
        # train_epoch_acc += train_acc.item()

        y_pred_softmax = torch.log_softmax(output, dim=1)
        _, y_pred_tags = torch.max(y_pred_softmax, dim=1)

        y_preds.extend(y_pred_tags.cpu().tolist())
        y_trues.extend(data["target_tag"].tolist())

    print("Classification Report:")
    print(classification_report(y_trues, y_preds, target_names=list(enc_tag.classes_)))
    y_preds = enc_tag.inverse_transform(y_preds)
    y_trues = enc_tag.inverse_transform(y_trues)
    cm = confusion_matrix(y_trues, y_preds,)
    ax = plt.subplot()
    sns.heatmap(cm, annot=True, ax=ax, cmap="Blues", fmt="d")
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted Labels")
    ax.set_ylabel("True Labels")

    return train_epoch_loss / len(data_loader), train_epoch_acc / len(data_loader)
