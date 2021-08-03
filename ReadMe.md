# HTML conversion tool for PDF (for Windows)

## **OverView**
---
 HTML conversion tool for PDF (for Windows) </br>
 Create 2021.07</br>
 Author  : GENROKU@Karakuri-musha</br>
 License : See the license file for the license.</br>
 Python ver : Python 3.8.10 (conda)</br>
 Hardware : Windows10

このツールは、PDF文書から英文を抜き出してテキストファイルに出力するツールです。</br>
このツールは、Windows10 で、PDFファイルから英文を取り出し、htmlファイルとして保存します。</br>
ツール処理完了後にhtmlファイルをブラウザで表示し、ブラウザの翻訳機能を使うことで翻訳することができます。  

This tool is a tool that extracts English text from a PDF document and outputs it to a text file. </br>
This tool extracts English text from PDF file and saves it as html file on Windows10. </br>
After the tool processing is completed, the html file can be displayed on the browser and translated by using the translation function of the browser.</br>
 </br>

以下のブログでこのツールを紹介しています。参考にしてください。（日本語）</br>
[【快適！Tools】英語のPDFをブラウザで自動翻訳してみよう（英語資料の翻訳）</br>https://karakuri-musha.com/inside-technology/how-to-translate…sh-documents-pdf/](https://karakuri-musha.com/inside-technology/how-to-translate…sh-documents-pdf/)

</br>

## **Tool file structure**
---
ツールのファイル構成は次の通りです。
</br>

|ファイル名  |形式  |説明  |
|---------|---------|---------|
|HtmlConv4PDF.py|Python3(.py)| ツール 本体です。Windows10上のPython環境にて実行してください。</br>The main body of the tool. Please execute in the Python environment on Windows 10.|
</br>


## **Run-time option specification**
---
ツール実行時に指定できるオプションは次の通りです。

[Execution example(for cmd)]</br>
`HtmlConv4PDF.exe -f conversion.pdf -o output.html
`

|option|Description|
|---------|---------|
| -f [file name] | 処理対象のPDFファイル名を指定します。</br> Specify the name of the PDF file to be processed.       |
| -o [file name] | 処理結果を保存するファイル名を指定します。</br> Specify the file name to save the processing result.      |

 </br>
 </br>

## **How to Log management**
---
ツール実行フォルダの配下に「Log」というフォルダを作成し出力されます。ログローテーション機能はありません。ツール実行につき1ファイル生成されます。

A folder called "Log" is created under the tool execution folder and output. There is no log rotation function. One file is generated for each tool execution.

 </br>
 </br>

## **How to use**
---



１．ツール格納用のフォルダをWindows10上に作成します。(例はC:\ドライブにToolsフォルダを作成）</br>
```
C:\User\User> mkdir Tools
C:\User\User> cd Tools
```
２．ブラウザで以下のGitHubにアクセスします。</br>
[https://github.com/karakuri-musha/HtmlConv4PDF.git](https://github.com/karakuri-musha/HtmlConv4PDF.git)


３．「Code」ボタンを押して、「Download zip」を押します。</br>

４．ダウンロードされたファイルを１で作ったフォルダに格納して展開します。

５．ツール格納用フォルダに変換するPDFをコピーします。

６．コマンドラインで、Pythonの実行環境を起動します。</br>
　　＊Windows10にインストールしたPythonの環境起動方法にしたがってください。</br>
　　＊Anaconda の場合、一般的に以下のコマンドでPythonの環境を起動できます。
```
C:\User\User\Tools> conda activate "PythonEnvName"
(PythonEnvName)C:\User\User\Tools>
```

７．前提となるライブラリをインストールします。
```
(PythonEnvName)C:\User\User\Tools> pip3 install PyMuPDF
```

８．ツールを実行します。</br>
（実行例：変換するPDF [ target.pdf ] 出力先ファイル名 [ output.html ）
```
(PythonEnvName)C:\User\User\Tools> python HtmlConv4PDF.py -f target.pdf -o output.html
```

９．実行後、以下のフォルダが作成され、処理結果が格納されます。
```
Log           →実行結果ログが格納されます。
result_files　→実行結果（返還後のHtml）が格納されます。
```


以下のブログでこのツールを紹介しています。参考にしてください。（日本語）</br>
[【快適！Tools】英語のPDFをブラウザで自動翻訳してみよう（英語資料の翻訳）</br>https://karakuri-musha.com/inside-technology/how-to-translate…sh-documents-pdf/](https://karakuri-musha.com/inside-technology/how-to-translate…sh-documents-pdf/)

</br>