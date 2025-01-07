import cv2
import numpy as np
import os

def smooth_red_edges(image_path, output_path):
    print(f"读取图片：{image_path}")
    # 使用imdecode读取图片
    img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"无法读取图片：{image_path}")
    
    print(f"图片尺寸：{img.shape}")
    
    # 转换到HSV空间以便处理红色区域
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 定义红色范围（调整以更好地匹配目标红色）
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # 创建红色掩码
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # 对掩码进行形态学操作
    kernel = np.ones((3,3), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 创建边缘过渡区域
    dilated_mask = cv2.dilate(red_mask, kernel, iterations=2)
    edge_mask = cv2.subtract(dilated_mask, red_mask)
    
    # 增强红色区域
    enhanced = img.copy()
    # 分离通道
    b, g, r = cv2.split(enhanced)
    # 增强红色通道
    r_enhanced = cv2.addWeighted(r, 1.2, np.zeros_like(r), 0, 5)  # 增加红色强度和亮度
    # 降低其他通道
    b_reduced = cv2.addWeighted(b, 0.9, np.zeros_like(b), 0, -5)
    g_reduced = cv2.addWeighted(g, 0.9, np.zeros_like(g), 0, -5)
    # 合并通道
    enhanced = cv2.merge([b_reduced, g_reduced, r_enhanced])
    
    # 对图像进行平滑处理
    # 1. 先进行高斯模糊
    blurred = cv2.GaussianBlur(enhanced, (5,5), 0)
    # 2. 使用双边滤波
    smoothed = cv2.bilateralFilter(blurred, 9, 100, 100)
    # 3. 对边缘区域进行额外的平滑
    edge_smooth = cv2.GaussianBlur(smoothed, (7,7), 0)
    
    # 组合结果
    result = img.copy()
    # 处理主要红色区域
    result[red_mask > 0] = smoothed[red_mask > 0]
    
    # 处理边缘过渡区域
    edge_region = edge_mask > 0
    result[edge_region] = cv2.addWeighted(img, 0.4, edge_smooth, 0.6, 0)[edge_region]
    
    # 最后进行轻微的全局平滑
    result = cv2.bilateralFilter(result, 7, 50, 50)
    result = cv2.GaussianBlur(result, (3,3), 0)
    
    # 最终的颜色调整
    b, g, r = cv2.split(result)
    r = cv2.addWeighted(r, 1.1, np.zeros_like(r), 0, 3)  # 最后再次轻微增强红色
    result = cv2.merge([b, g, r])
    
    # 保存结果
    print(f"保存结果到：{output_path}")
    _, buffer = cv2.imencode('.jpg', result)
    buffer.tofile(output_path)
    
    # 创建对比图像
    comparison = np.hstack([img, result])
    cv2.imencode('.jpg', comparison)[1].tofile('comparison.jpg')
    
    return True

if __name__ == "__main__":
    try:
        print("程序开始执行")
        print(f"当前工作目录：{os.getcwd()}")
        
        input_image = "da71e2d7d3721479ed63133b4bb5615.jpg"
        output_image = "smoothed_result2.jpg"
        
        if not os.path.exists(input_image):
            print(f"错误：输入文件不存在：{input_image}")
            print("目录中的文件：")
            for file in os.listdir():
                print(f"  - {file}")
            exit(1)
        
        print("\n开始处理图片...")
        success = smooth_red_edges(input_image, output_image)
        if success:
            print("处理完成！")
    except Exception as e:
        print(f"处理失败：{str(e)}")
        import traceback
        traceback.print_exc() 