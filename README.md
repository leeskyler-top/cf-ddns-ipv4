# Cloudflare DDNS Python Script

## 需要准备

### 第一步：获取Token

1. 登录[Cloudflare](https://dash.cloudflare.com)。
2. 前往 https://dash.cloudflare.com/profile/api-tokens 创建Token。
    1. 点击"创建令牌"按钮。
    2. 在"编辑区域 DNS"一栏单击"使用模板按钮"。
    3. 在"权限"一栏中分别选择 "区域" "DNS" "查看"。
    4. 单击"权限"一栏中的"+添加更多"超链接，分别选择 "区域" "DNS" "编辑"。
    5. 在"区域资源"一栏中，根据自身需求进行选择和配置。
    6. 在"TTL"一栏中，根据自身需求进行选择和配置，到期时间越久，今后所获取到Token需要更新的次数就越少，但安全问题也可能会随之增加。（对于部分进阶用户而言）
    7. 单击"显示令牌"将获取到的令牌复制保存

### 第二步：准备环境

*省去Python的安装步骤（请自行搜索自己的系统对应的安装方式）

最低版本要求: Python3.8, pip3

### 第三步：在设备上下载脚本

1. cd到想要将脚本存放的目录，以/var/cf_ddns/为例
   ```shell
   mkdir -p /var/cf_ddns/
   cd /var/cf_ddns
   ```
2. 下载git工具（如果有可忽略步骤）（请自行搜索自己的系统对应的安装方式）。
3. 克隆项目（下载脚本）
   ```shell
   git clone https://github.com/leeskyler-top/cf-ddns-ipv4.git
   ```

## 部署

### 部署脚本

1. 按需修改config.json

   config.json需要与main.py在同一目录，进阶用户请自行修改代码。

   字段解释：
    - get_ip_api

      获取公网IP的API

    - get_ip_api_key

      公网IP字段的键值对的键值，此字段被设置为""时，说明API返回的不是json，需要使用正则获取。

    - get_ip_api_regex

      获取IP的正则表达式，当"get_ip_api_key"字段被填写，此栏目不再有效。

    - token

      Cloudflare API令牌，将复制的令牌填写于此。

    - domain

      Zone区域，一级域名。

    - ddns_domain

      记录名称

   样例见config.example.json文件
2. 安装requests库
    ```shell
   pip3 install requests
    ```
3. 设置定时
   #### Windows
    1. 创建批处理文件
        
       为了更方便地执行 Python 脚本，您可以创建一个批处理文件（.bat 文件）来运行 Python 脚本。
          ```shell
          @echo off
          "C:\path\to\python.exe" "C:\path\to\main.py"
          ```
       请注意：```C:\path\to\python.exe``` 应修改为您Python的安装路径。
        
       请注意：```C:\path\to\main.py```应修改为您脚本的路径。
        
       保存为"ddns.bat"
    2. 使用任务计划程序创建任务
        
        1. 打开任务计划程序：
        
           按下 Windows + R 键，输入 ```taskschd.msc```，然后按回车。
        
        2. 创建基本任务：
           在任务计划程序窗口右侧，点击“创建基本任务”。
            
           输入任务名称和描述，例如“每 15 分钟运行 Python 脚本”。
            
        3. 设置触发器：
            
           选择“每日”触发。
            
           在下一个窗口中，选择“重复任务间隔”，并设置为 15 分钟。
            
        4. 选择操作：
            
           选择“启动程序”。
            
           点击“下一步”。
            
        5. 指定程序/脚本：
            
           在“程序/脚本”栏中，输入批处理文件的路径，例如 ```C:\path\to\ddns.bat```。
            
           请注意：```C:\path\to\ddns.bat```应修改为您脚本的路径。
            
        6. 完成
        
   #### Linux(crontab) （编辑器不同，这里不做保存退出操作演示）
   ```shell
   crontab -e
   ```
   每15分钟执行
   ```shell
   */15 * * * * /usr/bin/python3.11 /var/cf_ddns/main.py
   ```
    请注意：```/usr/bin/python3.11```应修改为您python的路径，注意部分系统自带python2，要另行安装python或指定版本号。
    
    请注意：```/var/cf_ddns/main.py```应修改为您脚本的路径。
    
### 部署IP获取脚本
            
#### 对于第三方获取公网IP不信任的使用者，如果有公网可访问的设备或虚拟主机，可以用简短的PHP脚本自己制作一个API。
            
*省去Nginx与PHP的安装步骤（请自行搜索自己的系统对应的安装方式）
            
版本：对Nginx或Apache和PHP的版本要求都不高，PHP版本5.4及以上即可。
            
- Nginx 伪静态与PHP配置，不提供完整的配置文件。
            
```
    location / {
        try_files $uri $uri/ /phpmyadmin/index.php?$args;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
```
请注意：php-fpm套接字文件的路径应修改为您自己的路径和版本。

- Apache 伪静态，不提供完整的配置文件。

```
<IfModule mod_rewrite.c>
    RewriteEngine On

    # Check if the requested file or directory does not exist
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d

    # Try adding .php extension if the request does not resolve to a file or directory
    RewriteCond %{DOCUMENT_ROOT}/$1.php -f
    RewriteRule ^(.*)$ /$1.php [QSA,L]
</IfModule>
```

## 代码审查

### 本脚本使用到的Cloudflare API:

- GET https://api.cloudflare.com/client/v4/user/tokens/verify
- GET https://api.cloudflare.com/client/v4/zones
- GET https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records
- POST https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records
- PATCH https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}

### API 官方文档
https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records