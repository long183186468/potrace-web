from flask import Flask, render_template, request, send_file, jsonify
import os
from PIL import Image
import subprocess
import tempfile
import base64
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
# 扩展支持的输入格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'pbm', 'pgm', 'ppm', 'pnm'}

# 支持的输出格式
OUTPUT_FORMATS = {
    'svg': {'ext': 'svg', 'flag': '-s', 'description': 'SVG 矢量图'},
    'dxf': {'ext': 'dxf', 'flag': '-b dxf', 'description': 'DXF 工程制图格式'},
    'pdf': {'ext': 'pdf', 'flag': '-b pdf', 'description': 'PDF 文档'},
    'eps': {'ext': 'eps', 'flag': '-b eps', 'description': 'EPS 矢量图'}
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/preview', methods=['POST'])
def preview():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        temp_img = None
        output_svg = None
        try:
            # 获取参数
            blacklevel = request.form.get('blacklevel', '0.5')
            turdsize = request.form.get('turdsize', '2')
            alphamax = request.form.get('alphamax', '1')
            opttolerance = request.form.get('opttolerance', '0.2')
            color = request.form.get('color', '').strip()
            outline_only = request.form.get('outline_only', 'false') == 'true'
            
            print(f"Debug - Parameters: blacklevel={blacklevel}, turdsize={turdsize}, alphamax={alphamax}, opttolerance={opttolerance}")
            
            # 创建临时文件
            temp_img = tempfile.NamedTemporaryFile(suffix='.pnm', delete=False)
            try:
                # 保存上传的图片并转换为PNM
                img = Image.open(file)
                # 对于剪纸图片（白底红色），提取红色图案
                if img.mode == 'RGB' or img.mode == 'RGBA':
                    # 转换为RGB确保格式统一
                    img = img.convert('RGB')
                    width, height = img.size
                    pixels = img.load()
                    # 创建新的二值图像
                    binary = Image.new('1', (width, height), 1)  # 1 = white
                    binary_pixels = binary.load()
                    
                    # 设置红色检测的阈值
                    red_threshold = 100
                    red_dominance = 30  # 红色比其他通道要强多少
                    
                    # 遍历每个像素
                    for y in range(height):
                        for x in range(width):
                            r, g, b = pixels[x, y]
                            # 检测红色：红色通道值高，且明显高于其他通道
                            if r > red_threshold and r > g + red_dominance and r > b + red_dominance:
                                binary_pixels[x, y] = 0  # 0 = black
                
                    img = binary
                
                # 保存为PNM
                img.save(temp_img.name)
                print(f"Debug - Image saved to: {temp_img.name}")
                
                # 创建输出SVG文件
                output_svg = os.path.join(UPLOAD_FOLDER, 'preview.svg')
                
                # 构建potrace命令
                cmd = ['potrace', temp_img.name, 
                      '-s',  # 预览始终使用SVG
                      '-o', output_svg,
                      '-k', str(blacklevel),
                      '-t', str(turdsize),
                      '-a', str(alphamax),
                      '-n',  # 不优化曲线，保持更多细节
                      '-O', str(opttolerance),
                      '-u', '10']  # 设置更高的精度
                
                if outline_only:
                    cmd.append('--opaque')
                
                if color:
                    # 确保颜色值有#前缀
                    clean_color = color.replace('#', '')
                    if len(clean_color) == 6:  # 确保是有效的6位十六进制颜色
                        cmd.extend(['-C', f'#{clean_color}'])
                
                print(f"Debug - Command: {' '.join(cmd)}")
                
                # 调用potrace进行转换
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Debug - Potrace error: {result.stderr}")
                    raise Exception(f"Potrace error: {result.stderr}")
                
                print(f"Debug - Potrace output: {result.stdout}")
                
                # 检查输出文件是否存在
                if not os.path.exists(output_svg):
                    raise Exception("Output SVG file was not created")
                
                # 读取SVG内容
                with open(output_svg, 'r') as f:
                    svg_content = f.read()
                
                return jsonify({'success': True, 'svg': svg_content})
                
            finally:
                # 清理临时文件
                if temp_img and os.path.exists(temp_img.name):
                    os.unlink(temp_img.name)
                if output_svg and os.path.exists(output_svg):
                    os.unlink(output_svg)
                
        except Exception as e:
            print(f"Debug - Error during processing: {str(e)}")
            return jsonify({'error': str(e)})
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        
        if file and allowed_file(file.filename):
            temp_img = None
            output_file = None
            temp_dxf = None
            try:
                # 获取用户选择的输出格式和选项
                output_format = request.form.get('output_format', 'svg')
                blacklevel = request.form.get('blacklevel', '0.5')
                turdsize = request.form.get('turdsize', '2')
                alphamax = request.form.get('alphamax', '1')
                opttolerance = request.form.get('opttolerance', '0.2')
                color = request.form.get('color', '').strip()
                outline_only = request.form.get('outline_only', 'false') == 'true'
                
                if output_format not in OUTPUT_FORMATS:
                    return 'Invalid output format'
                
                # 创建临时文件
                temp_img = tempfile.NamedTemporaryFile(suffix='.pnm', delete=False)
                
                # 保存上传的图片并转换为PNM
                img = Image.open(file)
                # 对于剪纸图片（白底红色），提取红色图案
                if img.mode == 'RGB' or img.mode == 'RGBA':
                    # 转换为RGB确保格式统一
                    img = img.convert('RGB')
                    width, height = img.size
                    pixels = img.load()
                    # 创建新的二值图像
                    binary = Image.new('1', (width, height), 1)  # 1 = white
                    binary_pixels = binary.load()
                    
                    # 设置红色检测的阈值
                    red_threshold = 100
                    red_dominance = 30  # 红色比其他通道要强多少
                    
                    # 遍历每个像素
                    for y in range(height):
                        for x in range(width):
                            r, g, b = pixels[x, y]
                            # 检测红色：红色通道值高，且明显高于其他通道
                            if r > red_threshold and r > g + red_dominance and r > b + red_dominance:
                                binary_pixels[x, y] = 0  # 0 = black
                
                    img = binary
                
                # 保存为PNM
                img.save(temp_img.name)
                
                # 创建输出文件
                output_ext = OUTPUT_FORMATS[output_format]['ext']
                output_file = os.path.join(UPLOAD_FOLDER, f'output.{output_ext}')
                
                # 构建potrace命令
                cmd = ['potrace', temp_img.name]

                # 添加输出格式标志
                cmd.extend(OUTPUT_FORMATS[output_format]['flag'].split())

                # 添加输出文件
                cmd.extend(['-o', output_file])

                # 添加基本参数
                cmd.extend([
                    '-k', str(blacklevel),
                    '-t', str(turdsize),
                    '-a', str(alphamax),
                    '-O', str(opttolerance),
                    '-z', 'black'
                ])

                # 如果是 DXF 格式，添加特殊参数
                if output_format == 'dxf':
                    cmd.extend([
                        '-u', '1',      # 设置单位为毫米
                        '-n',          # 禁用优化
                        '-a', '0',     # 禁用角度优化
                        '-O', '0',     # 禁用曲线优化
                        '--alphamax', '0',  # 最大角度设为0，保持所有角点
                        '--opaque'     # 只输出轮廓线
                    ])

                # 添加其他选项
                if outline_only:
                    cmd.append('--opaque')

                if color and output_format in ['svg', 'pdf', 'eps', 'postscript']:
                    clean_color = color.replace('#', '')
                    if len(clean_color) == 6:  # 确保是有效的6位十六进制颜色
                        cmd.extend(['-C', f'#{clean_color}'])
                
                # 调用potrace进行转换
                print(f"Debug - Running command: {' '.join(cmd)}")  # 添加调试输出
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Debug - Potrace error: {result.stderr}")  # 添加调试输出
                    raise Exception(f"Potrace error: {result.stderr}")
                
                # 检查输出文件是否存在和大小
                if not os.path.exists(output_file):
                    raise Exception("Output file was not created")
                
                file_size = os.path.getsize(output_file)
                print(f"Debug - Output file size: {file_size} bytes")  # 添加调试输出
                
                if file_size == 0:
                    raise Exception("Output file is empty")
                
                # 读取文件内容到内存
                with open(output_file, 'rb') as f:
                    file_content = f.read()
                
                # 清理临时文件
                if temp_img and os.path.exists(temp_img.name):
                    os.unlink(temp_img.name)
                if output_file and os.path.exists(output_file):
                    os.unlink(output_file)
                
                # 从内存发送文件
                return send_file(
                    BytesIO(file_content),
                    as_attachment=True,
                    download_name=f'converted.{output_ext}',
                    mimetype='application/octet-stream'
                )
                
            except Exception as e:
                print(f"Debug - Error during conversion: {str(e)}")  # 添加调试输出
                return f'Error during conversion: {str(e)}'
            
            finally:
                # 清理临时文件
                if temp_img and os.path.exists(temp_img.name):
                    os.unlink(temp_img.name)
                if temp_dxf and os.path.exists(temp_dxf):
                    os.unlink(temp_dxf)
            
    return render_template('upload.html', output_formats=OUTPUT_FORMATS.keys())

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, debug=True) 