# XcodeAutoBuild
Xcode自动打包并上传蒲公英平台

##介绍
工作中，特别是所做项目进入测试阶段，肯定会经常打 Ad-hoc 包给测试人员进行测试，但是我们肯定不想每次进行打包的时候都要进行一些工程的设置修改，以及一系列的 next 按钮点击操作，现在就让这些操作都交给脚本化吧!

1. 脚本化中使用如下的命令打包:
```
xcodebuild -project name.xcodeproj -target targetname -configuration Release -sdk iphoneos `

xcodebuild -workspace name.xcworkspace -scheme schemename -configuration Release -sdk iphoneos
```

2. 然后使用 exportArchive 生成 ipa 文件:
```
xcodebuild -exportArchive -archivePath archiveName.xcarchive 
                          -exportPath filePath 
                          -exportOptionsPlist exprotOptionsPlist.plist 
```
3. 清除 build 过程中产生的中间文件
4. 结合蒲公英分发平台，将 ipa 文件上传至蒲公英分发平台，同时在终端会打印上传结果以及上传应用后该应用的 URL。蒲公英分发平台能够方便地将 ipa 文件尽快分发到测试人员，该平台有开放 API，可避免人工上传。

##autobuild.py ：
###打包变量
```
Usage: autobuild.py [options]

Options:
-h, --help            show this help message and exit
-w name.xcworkspace, --workspace=name.xcworkspace
Build the workspace name.xcworkspace.
-p name.xcodeproj, --project=name.xcodeproj
Build the project name.xcodeproj.
-s schemename, --scheme=schemename
Build the scheme specified by schemename. Required if
building a workspace.
-t targetname, --target=targetname
Build the target specified by targetname. Required if
building a project.
-o output_filename, --output=output_filename
specify output filename
```
在脚本顶部，有几个全局变量，根据自己的项目情况修改。
```
WORKSPACE_PATH = 'XXXX.xcworkspace'
SCHEME_NAME = 'XXXXXXXXXX'
CODE_SIGN_IDENTITY = "iPhone Distribution: companyname (9xxxxxxx9A)"
PROVISIONING_PROFILE = "xxxxx-xxxx-xxx-xxxx-xxxxxxxxx"
CONFIGURATION = "Release"
SDK = "iphoneos"
EXPORT_OPTIONS_PLIST = 'ExportOptions.plist' #配置plist的method provisioningProfiles signingCertificate teamID 必须一一对应
OUTPUT_IPA_PATH = '/Users/XXXXX/Desktop/'#是否输出ipa到指定位置进行保存
```
其中，`CODE_SIGN_IDENTITY` 为开发者证书标识，可以在 钥匙串访问 ->证书 -> 选中证书右键弹出菜单 -> 显示简介 -> 常用名称 获取，类似 `iPhone Distribution: Company name Co. Ltd (xxxxxxxx9A)`, 包括括号内的内容。

`PROVISIONING_PROFILE`: 这个是 mobileprovision 文件的 identifier，获取方式：
Xcode -> Preferences -> 选中申请开发者证书的 Apple ID -> 选中开发者证书 -> View Details… -> 根据 Provisioning Profiles 的名字选中打包所需的 mobileprovision 文件 -> 右键菜单 -> Show in Finder -> 找到该文件后，除了该文件后缀名的字符串就是 `PROVISIONING_PROFILE` 字段的内容。
如果Xcode中不配置证书，则设置为空字符串：`CODE_SIGN_IDENTITY=''，PROVISIONING_PROFILE=''`，就自动不使用指定证书打包。

###蒲公英上传变量
```
# configuration for pgyer
PGYER_UPLOAD_URL = "https://www.pgyer.com/apiv2/app/upload"
DOWNLOAD_BASE_URL = "http://www.pgyer.com"
USER_KEY = "26dd239e2a66421b33efbe75258fa778"
API_KEY = "531620d42ff23590948175eb4999b42b"
BUILD_INSTALL_TYPE = '2' #1：公开，2：密码安装，3：邀请安装，4：回答问题安装。默认为1公开
BUILD_PASSWORD = '555555'
BUILD_DESCRIPTION = '测试PY上传'
```
`USER_KEY` `API_KEY` : 是蒲公英开放 API 的密钥。
`BUILD_INSTALL_TYPE` `BUILD_PASSWORD` `BUILD_DESCRIPTION`: 是给测试用户的安装方式和版本更新描述
