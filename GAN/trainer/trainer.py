import wandb
from tqdm import tqdm

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from GAN.datasets import InMemoryArtBench10_256x256


from piq import FID, SSIMLoss

from GAN.utils.utils import make_train_image, make_test_image


class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_inf_dataloader: DataLoader,
        test_dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        lr_scheduler: torch.optim.lr_scheduler.LinearLR,
        writer,
        save_dir: str,
        device: torch.device,
        config,
        epochs: int,
        iterations_per_epoch: int,
        save_period: int = 1,
        log_every_step: int = 100,
    ):
        self.model = model
        self.train_inf_dataloader = train_inf_dataloader
        self.test_dataloader = test_dataloader
        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler
        self.writer = writer
        self.save_dir = save_dir
        self.device = device
        self.epochs = epochs
        self.iterations_per_epoch = iterations_per_epoch
        self.save_period = save_period
        self.log_every_step = log_every_step

        self.fixed_noise = torch.randn(len(test_dataloader.dataset), config["model"]["args"]["latent_dim"], device=self.device)
        self.fid_metric = FID()
        self.ssim_metric = SSIMLoss(data_range=1.)
        

    def move_batch_to_device(self, batch):
        for key in ["img", "target"]:
            batch[key] = batch[key].to(self.device)

    def train_epoch(self):
        self.model.train()
        for batch_idx, batch in enumerate(self.train_inf_dataloader):
            log_wandb = {"learning_rate": self.lr_scheduler.get_last_lr()[0]}
            self.optimizer.zero_grad()

            self.move_batch_to_device(batch)
            output = self.model.train_batch(**batch)
            # model.train, because diffusion training pipeline differs from VAE training pipeline
            batch.update(output)

            loss = self.model.loss_function(**batch)
            for k, v in loss.items():
                log_wandb.update({k: v.item()})
            loss["loss"].backward()

            self.optimizer.step()
            self.lr_scheduler.step()

            if (batch_idx + 1) % self.log_every_step == 0:
                reconstructed_train_images = make_train_image((batch["pred"].detach().cpu().numpy() + 1) / 2, 4) * 255
                real_images = make_train_image((batch["img"].detach().cpu().numpy() + 1) / 2, 4) * 255
                log_wandb.update({"train": wandb.Image(np.concatenate([reconstructed_train_images, real_images]))})
            self.writer.log(log_wandb)

            if batch_idx + 1 == self.iterations_per_epoch:
                break

    def test(self):
        self.model.eval()
        last_idx = 0
        real_imgs = []
        constructed_imgs = []
        targets = []
        with torch.no_grad():
            for batch in self.test_dataloader:
                i = 0
                self.move_batch_to_device(batch)
                bs = batch["target"].shape[0]
                samples = self.model.sample(bs, batch["target"], z=self.fixed_noise[last_idx : last_idx + bs, ...])
                real_imgs.append(batch["img"].detach())
                constructed_imgs.append(samples.detach())
                targets.append(batch["target"].detach().cpu().numpy())
                last_idx += bs
                if i == 0:
                    real_images_dataset = InMemoryArtBench10_256x256(batch["img"].detach())
                    constructed_images_dataset = InMemoryArtBench10_256x256(samples.detach())
                    i += 1

        convert_to_01 = lambda imgs: (imgs + 1) / 2
        real_imgs = convert_to_01(torch.cat(real_imgs))
        constructed_imgs = convert_to_01(torch.cat(constructed_imgs))
        targets = np.concatenate(targets)
        
        # for FID score
        real_images_dataloader = DataLoader(real_images_dataset)
        constructed_images_dataloader = DataLoader(constructed_images_dataset)

        real_imgs_features = self.fid_metric.compute_feats(real_images_dataloader)
        constructed_imgs_features = self.fid_metric.compute_feats(constructed_images_dataloader)

        self.writer.log(
            {
                "test_FID": self.fid_metric(real_imgs_features, constructed_imgs_features).item(),
                "test_SSIM": self.ssim_metric(real_imgs, constructed_imgs).item(),
                "test": wandb.Image(make_test_image(constructed_imgs.cpu().numpy(), targets)),
                "real": wandb.Image(make_test_image(real_imgs.cpu().numpy(), targets)),
            },
            False,
        )

    def log_after_training_epoch(self, epoch):
        print(16 * "-")
        print(f"epoch:\t{epoch}")
        print(f"learning_rate:\t{self.lr_scheduler.get_last_lr()[0]:.8f}")
        print(16 * "-")

    def save_state(self, epoch):
        state = {
            "epoch": epoch,
            "state_dict": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "lr_scheduler": self.lr_scheduler.state_dict(),
        }
        torch.save(state, f"{self.save_dir}/checkpoint-{epoch}.pth")

    def train(self):
        """
        Training loop.
        """

        for epoch in tqdm(range(1, self.epochs + 1)):
            self.train_epoch()
            self.log_after_training_epoch(epoch)
            self.test()

            if epoch % self.save_period == 0:
                self.save_state(epoch)

        self.writer.finish()
