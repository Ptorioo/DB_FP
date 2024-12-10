# 113-1 Database Management - 筆知

## Introduction

你是否也曾在創作文章時覺得缺少共鳴？「筆知」是一個為文章創作者提供交流和互相學習的線上平台，讓擁有共同興趣和經歷的人們能夠在這裡分享想法、撰寫文章、閱讀別人的作品，並進行互動留言，打造充滿活力的文章社群。不論你是希望尋找志同道合的朋友，還是需要不同觀點來激發創意，「筆知」都能幫助你找到最適合的夥伴！

:link: **[展示影片連結](https://youtu.be/AxJEC0WS7ME)**

## Features

### Users

#### 瀏覽文章與留言

- 使用者可瀏覽平台上所有公開的文章與留言，這些文章會出現於首頁。

#### 新增文章

- 使用者可透過編輯文章內容、設定標題來發表新文章，每篇新增的文章皆會被賦予唯一編號以供識別，並儲存至資料庫中。

#### 儲存文章

- 使用者可儲存自己喜愛的文章，這些文章會出現於使用者的個人頁面。

#### 分享文章

- 使用者可分享喜愛的文章，轉貼到其它平台。

#### 查詢文章

- 使用者可透過標題、關鍵字搜尋系統中的文章，並瀏覽符合搜尋條件的文章列表。

#### 封存文章

- 使用者可封存自己發表的文章，這些文章將不會出現於公開頁面。

#### 瀏覽個人頁面

- 使用者可瀏覽個人頁面，瀏覽已儲存的文章和追蹤的創作者所發佈的文章。

#### 新增留言

- 使用者可於他人文章下方新增留言，分享感想、回饋建議或交流意見，每則留言會立即儲存至資料庫。

#### 追蹤他人

- 使用者可追蹤自己喜愛的創作者，已追蹤的創作者文章將會顯示於個人頁面。

#### 舉報他人

- 若使用者發現不適當的文章或留言內容，可進行舉報，系統將自動通知管理員（Admin）審查該內容並依情況處理。

#### 更改密碼與電子郵件

- 使用者可修改註冊的密碼與電子郵件。

### Admin

#### 管理文章

- 管理員可以查看平台上所有使用者發表的文章，對於違反平台規範的內容（如不當言論或敏感話題），管理員可執行封存或刪除的操作。

#### 管理留言

- 管理員可以監控所有留言互動，若發現不當留言，可進行刪除，以維護平台良好的交流環境。

#### 管理帳號

- 管理員擁有帳號管理權限，能查看所有使用者的基本資料、發表的文章數、留言數及舉報記錄。對於多次違反規範的帳號，管理員可執行禁言、限制發文或永久停用的處理。

#### 查詢舉報

- 管理員可以查看所有舉報記錄，包含被舉報的文章或留言內容、舉報原因及舉報次數。根據舉報的詳細情況，管理員可進行審核並決定是否採取進一步行動。

#### 管理舉報

- 根據舉報的詳細情況，管理員可進行審核並改變舉報目前的狀態 (審核中或已審核)。

## Installation

1. Make sure to have python installed.
2. Run `pip install -r requirements.txt` from root folder.
3. Restore data to database from file `DB_FP`
4. Run server at entry point: `./server/init.py`
5. Run client at entry point: `./client/init.py`

- Remember to setup environmental variables PORT and PASSWORD for your database.

- If you like to start off with an empty database, you can use CREATE_TABLES.sql to create tables. And DB_Code contains code which is used for data generation.

## Structure

- `./backup/`: Folder for past database backup files
- `./client/`: Folder for client code
- `DB_Code`: Folder for code used to generate data
- `./server/`: Folder for server code
- `./client/action/`: Functions that performs action (features)
- `./server/utils/`: Utility functions for server
- `CREATE_TABLES.sql`: SQL queries for table creation
- `DB_FP`: Database backup file
- `requirements.txt`: List of required dependencies

## Environment

- Windows 11

- Python: 3.11

  - psycopg2: 2.9.9
  - python-dotenv: 1.0.1

- PostgreSQL: 16
