import ultralytics as ul

# 加载预训练模型
model = ul.YOLO("yolo11n.pt")

# 开始训练
results = model.train(
    data="dataset.yaml",  # 数据集配置文件
    epochs=50,            # 训练轮数
    imgsz=640,           # 图片大小
    batch=16,            # batch大小
    device="0",          # 使用GPU，如果是CPU则设为"cpu"
    workers=8,           # 数据加载的工作进程数
    project="ygo_train", # 项目名称
    name="exp1",         # 实验名称
    exist_ok=True,       # 允许覆盖已存在的实验目录
    pretrained=True,     # 使用预训练权重
    optimizer="auto",    # 优化器
    verbose=True,        # 显示详细信息
    seed=0,              # 随机种子
    deterministic=True,  # 确定性训练
    single_cls=False,    # 关闭单类别模式
    rect=False,          # 矩形训练
    cos_lr=True,         # 余弦学习率调度
    close_mosaic=10,     # 最后10个epoch关闭mosaic增强
    resume=False,        # 是否从断点继续训练
    amp=True,            # 混合精度训练
    fraction=1.0,        # 使用数据集的比例
    label_smoothing=0.1, # 标签平滑
    nbs=64,              # 标称batch大小
    overlap_mask=True,   # 重叠掩码
    mask_ratio=4,        # 掩码下采样率
    dropout=0.1,         # 使用dropout正则化
    val=True,            # 验证
    save=True,           # 保存最佳模型
    save_json=False,     # 保存JSON格式的预测结果
    save_hybrid=False,   # 保存混合标签
    conf=0.25,           # NMS置信度阈值
    iou=0.45,            # NMS IoU阈值
    max_det=300,         # 每张图像的最大检测数
    half=False,          # 使用FP16推理
    dnn=False,           # 使用OpenCV DNN推理
    plots=True,          # 保存训练图表
) 