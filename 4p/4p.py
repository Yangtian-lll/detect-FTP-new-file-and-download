# coding = utf-8
"""
检测FTP服务器上指定路径文件夹文件，若更新则下载到本地
并将含zip的文件解压到指定目录下
"""
import ftplib
import os
import time
import zipfile

hostname = ""
username = ""
password = ""
local_file_path = ""
remote_file_path = ""


def connect_ftp():
    ftp = ftplib.FTP(hostname, username, password)
    ftp.cwd("/")
    return ftp


def check_file_update(ftp):
    old_file_list = ftp.nlst()

    time.sleep(5)

    file_list = ftp.nlst()

    new_files = [f for f in file_list if f not in old_file_list]
    if new_files:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), f"发现 {len(new_files)} 个新文件：{new_files}")
        new_files_names = "\n".join(new_files)
        return new_files_names
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "no new file")
        ftp.quit()


def download_new_file(ftp, local_file_path, remote_file_path):
    response = ftp.retrbinary('RETR %s' % remote_file_path, open(local_file_path, "wb").write)
    print(response)
    ftp.quit()
    if "226" in response:
        print("wait for 10s")
        time.sleep(10)
        return 1


def unzip_files():
    zip_path = os.path.join(local_file_path, new_files_name)
    srcfile = zipfile.ZipFile(zip_path)
    desdir = zip_path[:zip_path.index('.zip')]
    for filename in srcfile.namelist():
        srcfile.extract(filename, desdir)
    print("1st file unzip complete")
    while True:
        r = 1
        for root, dirs, files in os.walk(desdir):
            isEnd = True
            for subFile in files:
                if subFile.endswith('.zip'):
                    isEnd = False
                subpath = root + '/' + subFile
                if zipfile.is_zipfile(subpath):
                    r = r + 1
                    print(f"start to unzip {r}st zip file")
                    subsrcfile = zipfile.ZipFile(subpath)
                    for subfilename in subsrcfile.namelist():
                        subsrcfile.extract(subfilename, root)
            if len(dirs) == 0 and not isEnd:
                break
        if isEnd:
            os.remove(zip_path)
            break


if __name__ == '__main__':
    while True:
        ftp = connect_ftp()
        new_files_name = check_file_update(ftp)
        if new_files_name is not None:
            isZip = download_new_file(ftp, os.path.join(local_file_path, new_files_name),
                                      os.path.join(remote_file_path + new_files_name))
            print("download complete")
            if isZip:
                print("start to unzip file")
                unzip_files()
