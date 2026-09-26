BaseModel = trainer.UNetNodeTransformer
reference = {}
class SecondaryFineTune(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_state_dict(initial_state, strict=True)
        reference["teacher"] = copy.deepcopy(self).cuda().eval().requires_grad_(False)
        self.requires_grad_(False)
        for module in (self.unet.decoder_blocks[-1], self.unet.head, self.detect_head): module.requires_grad_(True)
    def train(self, mode=True):
        return super().train(False)
    def encode(self, imgs):
        features, logits = super().encode(imgs)
        if torch.is_grad_enabled():
            with torch.no_grad(): teacher_features, teacher_logits = reference["teacher"].encode(imgs)
            reference["logits"] = iter(teacher_logits)
            reference["feature_loss"] = functional.mse_loss(features.float(), teacher_features.float()) / teacher_features.float().square().mean().clamp_min(1e-6)
        return features, logits
def sparse_detection_loss(logits, coords, mask, neg_weight=0.01):
    """结合标注中心监督、未标注区域蒸馏与共享特征约束。"""
    teacher_prob = next(reference["logits"]).float().sigmoid()
    points = coords[mask].long().clamp_min(0).minimum(torch.tensor(logits.shape[2:], device=logits.device) - 1)
    positive = torch.zeros_like(logits, dtype=torch.bool)
    positive[mask.nonzero()[:, 0], 0, points[:, 0], points[:, 1], points[:, 2]] = True
    positive_loss = functional.softplus(-logits.float())[positive].sum() / positive.sum().clamp_min(1)
    distillation = functional.binary_cross_entropy_with_logits(logits.float(), teacher_prob, reduction="none")
    return positive_loss + 0.5 * distillation[~positive].sum() / (~positive).sum().clamp_min(1) + 0.1 * reference["feature_loss"]
