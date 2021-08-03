
#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   HTML conversion tool for PDF                  Create 2021.07
#   for Windows 
#   このツールは、Windows10 で、PDFファイルから英文を取り出し、htmlファイルとして
#   保存します。ツール処理完了後にhtmlファイルをブラウザで表示し、ブラウザの翻訳機能
# 　を使うことで翻訳することができます。  
#
#   オプション指定  
#     -f [file name] ：処理対象のPDFファイル名を指定します。
#     -o [file name] : 処理結果を保存するファイル名を指定します。
#
#   処理結果出力　
#   　出力：処理結果は、ツール実行フォルダの配下に「result_files」フォルダを生成し
# 　　　　　出力されます。生成ファイル名は、実行時に[-o] オプションで指定した名前です。
# 　　ログ：ツール実行フォルダの配下に「Log」というフォルダを作成し出力されます。
# 　　　　　ログローテーション機能はありません。ツール実行につき1ファイル生成されます。
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#
#   Reference 
#       pyMuPDF : https://pypi.org/project/PyMuPDF/
#                 https://pymupdf.readthedocs.io/en/latest/
#       
#-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
# ライブラリインポート部 
# -------------------------------------------------------------------------------------------
# 共通ライブラリ
import sys
import os
from datetime import datetime
import subprocess
import json
import platform
import glob
import logging
from logging import FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
from argparse import ArgumentParser

# ツール独自利用ライブラリ
import fitz

# -------------------------------------------------------------------------------------------
# 変数/定数　定義部 
# -------------------------------------------------------------------------------------------
CMD_TEXT =  'systeminfo'

SYSTEM_LABEL_RASPI          = 1
SYSTEM_LABEL_JETSON         = 2
SYSTEM_LABEL_LINUX          = 3
SYSTEM_LABEL_LINUX_OTHER    = 4
SYSTEM_LABEL_WIN10          = 5
SYSTEM_LABEL_WIN_OTHER      = 6

MSG_GET_OPTIONS_FILE_HELP         = "Specify the file (.pdf format) to be processed. "
MSG_GET_OPTIONS_OUTPUT_HELP       = "Specify the output file name (.html format) of the processing result. "

# -------------------------------------------------------------------------------------------
# 関数　定義部
# -------------------------------------------------------------------------------------------

# Windows向け　外部コマンドの実行処理用の関数　Function for executing external commands.
# Windowsはロケールによってコマンドプロンプトの言語設定が違うため、英語出力に変更して出力する
def win_call_subprocess_run(origin_cmd):
    try:
        # コマンドプロンプトの言語コードを確認し、変数chcp_originに格納
        pre_p = subprocess.Popen("chcp",
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        chcp_res, _ = pre_p.communicate()
        chcp_origin = chcp_res.split(':')

        # コマンドプロンプト起動時に言語コードを英語に変更して起動し、systeminfoを実行
        res = subprocess.Popen("cmd.exe /k \"chcp 437\"",
                            shell=True,
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        res.stdin.write(origin_cmd + "\n")
        stdout_t, _ = res.communicate()

        # コマンドプロンプトの言語コードをorigin_chcpに戻す
        cmd = "chcp " + str(chcp_origin[1])
        after_p = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        after_res, _ = after_p.communicate()
  
        for line in stdout_t.splitlines():
            yield line

    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + origin_cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# Linux/Raspberry Pi OS用の外部コマンド実行関数(1)
# 通常外部コマンドの実行処理用の関数　Function for executing external commands.
def call_subprocess_run(cmd):
    try:
        res = subprocess.run(cmd, 
                            shell=True, 
                            check=False,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
        for line in res.stdout.splitlines():
            yield line
    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# Linux/Raspberry Pi OS用の外部コマンド実行関数(2)
# Sudo系コマンドの実行処理用の関数　Function for executing external commands.
def call_subprocess_run_sudo(cmd, p_passphrase):
    try:
        res = subprocess.run(cmd, 
                            shell=True, 
                            check=True,
                            stdin=p_passphrase + '\n',
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
        for line in res.stdout.splitlines():
            yield line
    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# システム情報の取得
# Rassbery PiとJetson以外のLinuxで実行された場合に実行環境を取得するための処理
def get_system_data(p_passphrase):
    lshw_cmd = ['sudo', 'lshw', '-json']
    proc = subprocess.Popen(lshw_cmd, 
                            stdin=p_passphrase + '/n',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()[0]
# End Function

# Rassbery PiとJetson以外のLinuxで実行された場合に実行環境を読み込むための処理
def read_data(proc_output, class_='system'):
    proc_result = []
    proc_json = json.loads(proc_output)
    for entry in proc_json:
        proc_result.append(entry.get('product', ''))
    return proc_result
# End Function

# オプションの構成
def get_option():
    argparser = ArgumentParser()
    argparser.add_argument("-f", "--file", help=MSG_GET_OPTIONS_FILE_HELP)
    argparser.add_argument("-o", "--output", help=MSG_GET_OPTIONS_OUTPUT_HELP)
    return argparser.parse_args()
# End Function

# 外部ファイルの更新処理用の関数（先頭行追加）　Function for updating external files.
def update_file(p_file_d, p_data, p_dir_path):
    try:
        #指定されたファイルパスを元に更新元ファイルをバックアップ
        mk_dir_name = os.path.join(p_dir_path,'result_files')
        p_file_namepath = os.path.join(mk_dir_name, p_file_d)
        # --出力用ライブラリの所在確認と作成
        if not os.path.isdir(mk_dir_name):
            os.makedirs(mk_dir_name, exist_ok = True)
        #if os.path.exists(p_file_namepath):
        #    os.remove(p_file_namepath)

        logger.info('---- Update file ----')
        with open(p_file_namepath, "a") as fs:
            for line in p_data:
                str_text = line.replace('<h3>', '<p style=\"text-indent:2em\">').replace('</h3>', '</p>')
                fs.write(str_text)
        fs.close
        logger.info('---- Success update file ----')
        return 0
    except OSError as e:
        logger.error(e)
        fs.close
        return 1
# End Function

# -----------------------------------------------------------------------------
# main処理（main.pyが起動された場合に処理される内容）
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # ----------------------------------------------------------
    # Get Current path process
    # ----------------------------------------------------------
    # Current Path の取得
    # 実行方式（実行形式ファイル、または.pyファイル）によりカレントパスの取得方法を分ける
    if getattr(sys, 'frozen', False):
        os_current_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        os_current_path = os.path.dirname(os.path.abspath(__file__))
    dir_path = os_current_path

    # ----------------------------------------------------------
    # Set Logger process
    # ----------------------------------------------------------
    # ロギングの設定（ログファイルに出力する）
    # --ログ出力用ライブラリの所在確認と作成
    log_path = os.path.join(dir_path, "Log")
    if not os.path.isdir(log_path):
        os.makedirs(log_path, exist_ok = True)

    # --ファイル出力用ハンドラ
    file_handler = FileHandler(
        f"{log_path}/log{datetime.now():%Y%m%d%H%M%S}.log"
    )
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(
        Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
    )

    # --ルートロガーの設定
    logging.basicConfig(level=NOTSET, handlers=[file_handler])

    logger = logging.getLogger(__name__)
    logger.info('Make Report Tools from PDF tool is Start')

    # ---------------------------------------------------------------
    # Check option and file format. 
    # ---------------------------------------------------------------
    # コマンドで指定されたインストール定義ファイル名の確認
    args = get_option()
    input_file_name = args.file
    output_file_name = args.output
    
    p_filename, p_ext = os.path.splitext(input_file_name)
    if p_ext == '.pdf':
        logger.info('Input file is [' + input_file_name + '] I checked the file. The process will start.')
    else:
        logger.error('Input file is [' + input_file_name + '] The extension of the specified file is different. Please specify a .pdf format file.')   
        sys.exit() 

    p_outputname, p_outext = os.path.splitext(output_file_name)
    if p_outext == '.html':
        logger.info('Input file is [' + output_file_name + '] I checked the name. The process will start.')
    else:
        logger.error('Input file is [' + output_file_name + '] The extension of the specified file is different. Please specify a .html format file.')   
        sys.exit() 

    # ---------------------------------------------------------------
    # Check System environment 
    # ---------------------------------------------------------------
    # システム環境の判別 Determining the system environment.
    logger.info('System Enviroment Check Process Begin')

    system_label = ''
    os_name = platform.system()
    logger.info('The operating system is [' + os_name + ']')
    if os_name == 'Linux':
        # Raspberry Pi / Jetson / other ( have device-tree/model )
        if os.path.exists('/proc/device-tree/model'):
            res = call_subprocess_run('cat /proc/device-tree/model')
            os_info = res.__next__()
            if 'Raspberry Pi' in os_info:
                system_label = SYSTEM_LABEL_RASPI
                logger.info('The model name is [' + os_info + ']')
            elif 'NVIDIA Jetson' in os_info:
                system_label = SYSTEM_LABEL_JETSON
                logger.info('The model name is [' + os_info + ']　This environment is not supported. Exit the tool.')
                sys.exit()
            else:
                system_label = SYSTEM_LABEL_LINUX_OTHER
                logger.error('The model name is [' + os_info + ']　This environment is not supported. Exit the tool.')
                sys.exit()
        # Linux ( Not have device-tree/model )
        else:
            for product in read_data(get_system_data()):
                os_info = SYSTEM_LABEL_LINUX
            logger.error('The model name is [' + os_info + ']　This environment is not supported. Exit the tool.')
            sys.exit()

    elif os_name == 'Windows':
        systeminfo_l = win_call_subprocess_run(CMD_TEXT)
 
        systeminfo_dict = []
        for line in systeminfo_l:
            info_l = line.split(': ')
            for i in range(len(info_l)):
                info_l[i] = info_l[i].strip()
            systeminfo_dict.append(info_l)
        
        if 'Microsoft Windows 10' in systeminfo_dict[5][1]:
            system_label = SYSTEM_LABEL_WIN10
            logger.info('The model name is [' + systeminfo_dict[5][1] + ']')
        else:
            system_label = SYSTEM_LABEL_WIN_OTHER
            logger.error('The model name is [' + systeminfo_dict[5][1] + '] This environment is not supported. Exit the tool.')
            sys.exit()

    # ---------------------------------------------------------------
    # Tool main 処理部 
    # ---------------------------------------------------------------
    # 対象システムの指定
    if system_label == SYSTEM_LABEL_WIN10:
        try:
            # PDFファイルのOpen処理
            logger.info('PDF file open :' + input_file_name)
            doc = fitz.open(input_file_name)
        
            # Read File infomation
            d_metadata = doc.metadata
            logger.info(d_metadata)

            d_page_count = doc.page_count
            logger.info('This document file page count :' + str(d_page_count))

            d_toc = doc.get_toc()
            logger.info('Get the table of contents.')

            # ページごとの処理
            for pno in range(d_page_count):
                logger.info('Page loading and conversion [Page: ' + str(pno + 1) + ']')
                page = doc.load_page(pno)

                # PDFをbbox毎に分けてテキスト化する
                d_text = page.get_text("xhtml")

                update_file(output_file_name, d_text, dir_path)

            logger.info('The PDF file conversion process result is saved in the following file [file: ' + output_file_name + ']')
            doc.close()
        
        except OSError as e:
            logger.error(e)
            logger.error('[Page: '+ d_page_count + ']')
    
    logger.info('Make Report Tools from PDF tool is finished')

