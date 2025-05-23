# DeepSeek Chat 打包指南

## 打包步骤

### 方法一：使用批处理文件（推荐）

1. 双击运行 `package.bat`
2. 等待打包完成
3. 在 `dist` 文件夹中找到生成的 EXE 文件

### 方法二：手动打包

1. 安装依赖
```bash
pip install pyinstaller requests
```

2. 执行打包命令
```bash
pyinstaller deepseek.spec --onefile
```

3. 在 `dist` 文件夹中找到生成的 EXE 文件

## 注意事项

- 请确保打包前将 `icon.ico` 替换为有效的图标文件
- 默认情况下会使用 `api_config.json` 中的配置
- 如果需要更改图标，请修改 `deepseek.spec` 文件中的相应项
- 生成的 EXE 文件约为 10-20MB，包含所有依赖
- 打包过程需要安装 Python 和相关依赖 