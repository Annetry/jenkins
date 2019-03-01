import sys
from optparse import OptionParser
import subprocess
import requests


#configuration for iOS build setting
#WORKSPACE_PATH = 'XXXXXX.xcworkspace'
PROJECT_PATH='IfengNewsFull.xcodeproj'
SCHEME_NAME = 'IfengNews'
#开发者证书标识，可以在 钥匙串访问 ->证书 -> 选中证书右键弹出菜单 -> 显示简介 -> 常用名称
CODE_SIGN_IDENTITY = "iPhone Distribution: Yi Feng Lian He (Beijing) Technology Co., Ltd. (EFH38368XS)"
# PROVISIONING_PROFILE = "xxxxxxx-xxxxx-xxxx-xxxx-xxxxxxxxx" 如果使用Xcode自动管理Profile,直接留空就好
PROVISIONING_PROFILE = ""
CONFIGURATION = "Release"
SDK = "iphoneos"
EXPORT_OPTIONS_PLIST = 'ExportOptions.plist' #配置plist的method provisioningProfiles signingCertificate teamID 必须一一对应
OUTPUT_IPA_PATH = '/Users/wang/Desktop/'#是否输出ipa到指定位置进行保存


# configuration for pgyer
PGYER_UPLOAD_URL = "https://www.pgyer.com/app/publish"
DOWNLOAD_BASE_URL = "http://www.pgyer.com"
USER_KEY = "26dd239e2a66421b33efbe75258fa778"
API_KEY = "531620d42ff23590948175eb4999b42b"
BUILD_INSTALL_TYPE = '2' #1：公开，2：密码安装，3：邀请安装，4：回答问题安装。默认为1公开
BUILD_PASSWORD = '555555'
BUILD_DESCRIPTION = '测试PY上传'

def cleanBuildDir(buildDir):
    cleanCmd = "rm -r %s" %(buildDir)
    process = subprocess.Popen(cleanCmd, shell = True)
    process.wait()
    print ("cleaned buildDir: %s" %(buildDir))


def parserUploadResult(jsonResult):
    resultCode = jsonResult['code']
    if resultCode == 0:
        downUrl = DOWNLOAD_BASE_URL +"/"+jsonResult['data']['buildShortcutUrl']
        downLongUrl = jsonResult['data']['buildQRCodeURL']
        print ("Upload Success")
        print ("DownUrl is:" + downUrl)
        print("buildVersion :" + jsonResult['data']['buildBuildVersion'])
        print("QRCodeURL is:" + downLongUrl)

    else:
        print ("Upload Fail!")
        print ("Reason:"+jsonResult['message'])

def uploadIpaToPgyer(ipaPath):
    print ("ipaPath:"+ipaPath)
    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype':'multipart/form-data'}
    payload = {'uKey':USER_KEY,'_api_key':API_KEY,'buildInstallType':BUILD_INSTALL_TYPE,'buildPassword':BUILD_PASSWORD,'buildUpdateDescription':BUILD_DESCRIPTION}
    print ("uploading....")
    r = requests.post(PGYER_UPLOAD_URL, data = payload ,files=files,headers=headers)
    print(r)
    if r.status_code == requests.codes.ok:
        result = r.json()
        print(result)
        parserUploadResult(result)
    else:
        print ('HTTPError,Code:'+r.status_code)

def buildProject(project, target, output):
    if len(CODE_SIGN_IDENTITY) and len(PROVISIONING_PROFILE):
        buildCmd = 'xcodebuild archive -project %s -scheme %s -archivePath %s -sdk %s -configuration %s build CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" ' % (
        project, scheme, archivePath, SDK, CONFIGURATION, CODE_SIGN_IDENTITY, PROVISIONING_PROFILE)
        print (buildCmd)
        pass
    else:
        buildCmd = 'xcodebuild archive -project %s -scheme %s -sdk %s -archivePath %s -configuration %s ' % (project, scheme, SDK, archivePath, CONFIGURATION)
        print (buildCmd)
    
    process = subprocess.Popen(buildCmd, shell = True)
    process.wait()

    signCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" % (archivePath, buildDir, EXPORT_OPTIONS_PLIST)
    process = subprocess.Popen(signCmd, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    print('signResult:\n', stdoutdata, stderrdata)

    try:
        signCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" % (
        archivePath, OUTPUT_IPA_PATH, EXPORT_OPTIONS_PLIST)
        print(signCmd)
        process = subprocess.Popen(signCmd, shell=True)
        (stdoutdata, stderrdata) = process.communicate()
    except:
        pass

    uploadPath =  buildDir + '/' + scheme +'.ipa'
    uploadIpaToPgyer(uploadPath)
    cleanBuildDir(buildDir)

def buildWorkspace(workspace, scheme, output):
    process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()
    buildDir = stdoutdata.strip().decode() + '/build'
    print ("buildDir: " + buildDir)
    archivePath = buildDir + '/' + scheme +'.xcarchive'
    if len(CODE_SIGN_IDENTITY) and len(PROVISIONING_PROFILE):
        buildCmd = 'xcodebuild archive -workspace %s -scheme %s -archivePath %s -sdk %s -configuration %s build CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" ' %(workspace, scheme,archivePath , SDK, CONFIGURATION, CODE_SIGN_IDENTITY, PROVISIONING_PROFILE)
        print(buildCmd)
    else:
        buildCmd = 'xcodebuild archive -workspace %s -scheme %s -sdk %s -archivePath %s -configuration %s ' %(workspace, scheme, SDK, archivePath, CONFIGURATION)
        print(buildCmd)
    #进行归档
    process = subprocess.Popen(buildCmd, shell = True)
    process.wait()

    #打包
    signCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" %(archivePath, buildDir, EXPORT_OPTIONS_PLIST)
    print(signCmd)
    process = subprocess.Popen(signCmd, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
    print('signResult:\n',stdoutdata,stderrdata)

    try:
        signCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" % (
        archivePath, OUTPUT_IPA_PATH, EXPORT_OPTIONS_PLIST)
        print(signCmd)
        process = subprocess.Popen(signCmd, shell=True)
        (stdoutdata, stderrdata) = process.communicate()
    except:
        pass

    uploadPath =  buildDir + '/' + scheme +'.ipa'
    uploadIpaToPgyer(uploadPath)
    cleanBuildDir(buildDir)

def xcbuild(options):
    project = options.project
    workspace = options.workspace
    target = options.target
    scheme = options.scheme
    output = options.output

    if project is None and workspace is None:
        pass
    elif project is not None:
        buildProject(project, target, output)
    elif workspace is not None:
        buildWorkspace(workspace, scheme, output)

def main():
    
    parser = OptionParser()
    parser.add_option("-w", "--workspace", help="Build the workspace name.xcworkspace.", metavar="name.xcworkspace")
    parser.add_option("-p", "--project", help="Build the project name.xcodeproj.", metavar="name.xcodeproj")
    parser.add_option("-s", "--scheme", help="Build the scheme specified by schemename. Required if building a workspace.", metavar="schemename")
    parser.add_option("-t", "--target", help="Build the target specified by targetname. Required if building a project.", metavar="targetname")
    parser.add_option("-o", "--output", help="specify output filePath+filename", metavar="output_filePath+filename")

    arg = ['-w',WORKSPACE_PATH,'-s',SCHEME_NAME]
    print(arg)
    (options, args) = parser.parse_args(arg)
    print ("options: %s, args: %s" % (options, args))

    xcbuild(options)

if __name__ == '__main__':
    main()
